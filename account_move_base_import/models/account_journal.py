# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import sys
import traceback
import os
from odoo import _, api, fields, models
from ..parser.parser import new_move_parser
from odoo.exceptions import UserError, ValidationError


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal", "mail.thread"]
    _order = "sequence"

    used_for_import = fields.Boolean(string="Journal used for import")

    commission_account_id = fields.Many2one(
        comodel_name="account.account", string="Commission account"
    )

    import_type = fields.Selection(
        [("generic_csvxls_so", "Generic .csv/.xls based on SO Name")],
        string="Type of import",
        default="generic_csvxls_so",
        required=True,
        help="Choose here the method by which you want to import account "
        "moves for this journal.",
    )

    last_import_date = fields.Datetime(string="Last Import Date")

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Bank/Payment Office partner",
        help="Put a partner if you want to have it on the commission move "
        "(and optionaly on the counterpart of the intermediate/"
        "banking move if you tick the corresponding checkbox).",
    )

    receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Receivable/Payable Account",
        help="Choose a receivable/payable account to use as the default "
        "debit/credit account.",
    )

    used_for_completion = fields.Boolean(string="Journal used for completion")

    rule_ids = fields.Many2many(
        comodel_name="account.move.completion.rule",
        string="Auto-completion rules",
        relation="account_journal_completion_rule_rel",
    )

    launch_import_completion = fields.Boolean(
        string="Launch completion after import",
        help="Tic that box to automatically launch the completion "
        "on each imported file using this journal.",
    )

    create_counterpart = fields.Boolean(
        string="Create Counterpart",
        help="Tick that box to automatically create the move counterpart",
        default=True,
    )

    split_counterpart = fields.Boolean(
        string="Split Counterpart",
        help="Two counterparts will be automatically created : one for "
        "the refunds and one for the payments",
    )

    @api.multi
    def _prepare_counterpart_line(self, move, amount, date):
        if amount > 0.0:
            account_id = self.default_debit_account_id.id
            credit = 0.0
            debit = amount
        else:
            account_id = self.default_credit_account_id.id
            credit = -amount
            debit = 0.0
        counterpart_values = {
            "date_maturity": date,
            "credit": credit,
            "debit": debit,
            "partner_id": self.partner_id.id,
            "move_id": move.id,
            "account_id": account_id,
            "already_completed": True,
            "journal_id": self.id,
            "company_id": self.company_id.id,
            "currency_id": self.currency_id.id,
            "company_currency_id": self.company_id.currency_id.id,
            "amount_residual": amount,
        }
        return counterpart_values

    @api.multi
    def _create_counterpart(self, parser, move):
        move_line_obj = self.env["account.move.line"]
        refund = 0.0
        payment = 0.0
        transfer_lines = []
        for move_line in move.line_ids:
            refund -= move_line.debit
            payment += move_line.credit
        if self.split_counterpart:
            if refund:
                transfer_lines.append(refund)
            if payment:
                transfer_lines.append(payment)
        else:
            total_amount = refund + payment
            if total_amount:
                transfer_lines.append(total_amount)
        counterpart_date = (
            parser.get_move_vals().get("date") or fields.Date.today()
        )
        transfer_line_count = len(transfer_lines)
        check_move_validity = False
        for amount in transfer_lines:
            transfer_line_count -= 1
            if not transfer_line_count:
                check_move_validity = True
            vals = self._prepare_counterpart_line(
                move, amount, counterpart_date
            )
            move_line_obj.with_context(
                check_move_validity=check_move_validity
            ).create(vals)

    @api.multi
    def _write_extra_move_lines(self, parser, move):
        """Insert extra lines after the main statement lines.

        After the main statement lines have been created, you can override this
        method to create extra statement lines.

            :param:    browse_record of the current parser
            :param:    result_row_list: [{'key':value}]
            :param:    profile: browserecord of account.statement.profile
            :param:    statement_id: int/long of the current importing
              statement ID
            :param:    context: global context
        """
        move_line_obj = self.env["account.move.line"]
        global_commission_amount = 0
        for row in parser.result_row_list:
            global_commission_amount += float(
                row.get("commission_amount", "0.0")
            )
        partner_id = self.partner_id.id
        # Commission line
        if global_commission_amount > 0.0:
            raise UserError(_("Commission amount should not be positive."))
        elif global_commission_amount < 0.0:
            if not self.commission_account_id:
                raise UserError(
                    _("No commission account is set on the journal.")
                )
            else:
                commission_account_id = self.commission_account_id.id
                comm_values = {
                    "name": _("Commission line"),
                    "date_maturity": (
                        parser.get_move_vals().get("date")
                        or fields.Date.today()
                    ),
                    "debit": -global_commission_amount,
                    "partner_id": partner_id,
                    "move_id": move.id,
                    "account_id": commission_account_id,
                    "already_completed": True,
                }
                if (
                    self.currency_id
                    and self.currency_id != self.company_id.currency_id
                ):
                    # the commission we are reading is in the currency of the
                    # journal: use the amount in the amount_currency field, and
                    # set credit / debit to the value in company currency at
                    # the date of the move.
                    currency = self.currency_id.with_context(date=move.date)
                    company_currency = self.company_id.currency_id
                    comm_values["amount_currency"] = comm_values["debit"]
                    comm_values["debit"] = currency.compute(
                        comm_values["debit"], company_currency
                    )
                    comm_values["currency_id"] = currency.id
                move_line_obj.with_context(check_move_validity=False).create(
                    comm_values
                )

    @api.multi
    def write_logs_after_import(self, move, num_lines):
        """Write the log in the logger

        :param int/long statement_id: ID of the concerned
          account.bank.statement
        :param int/long num_lines: Number of line that have been parsed
        :return: True
        """
        self.message_post(
            body=_("Move %s have been imported with %s " "lines.")
            % (move.name, num_lines)
        )
        return True

    def prepare_move_line_vals(self, parser_vals, move):
        """Hook to build the values of a line from the parser returned values.
        At least it fulfills the basic values. Override it to add your own
        completion if needed.

        :param dict of vals from parser for account.bank.statement.line
          (called by parser.get_st_line_vals)
        :param int/long statement_id: ID of the concerned
          account.bank.statement
        :return: dict of vals that will be passed to create method of
          statement line.
        """
        move_line_obj = self.env["account.move.line"]
        values = parser_vals
        if not values.get("account_id", False):
            values["account_id"] = self.receivable_account_id.id
        account = self.env["account.account"].browse(values["account_id"])
        if (
            self.currency_id
            and self.currency_id != self.company_id.currency_id
        ):
            # the debit and credit we are reading are in the currency of the
            # journal: use the amount in the amount_currency field, and set
            # credit / debit to the value in company currency at the date of
            # the move.
            currency = self.currency_id.with_context(date=move.date)
            company_currency = self.company_id.currency_id
            values["amount_currency"] = values["debit"] - values["credit"]
            values["debit"] = currency.compute(
                values["debit"], company_currency
            )
            values["credit"] = currency.compute(
                values["credit"], company_currency
            )
        if account.reconcile:
            values["amount_residual"] = values["debit"] - values["credit"]
        else:
            values["amount_residual"] = 0
        values.update(
            {
                "company_id": self.company_id.id,
                "currency_id": self.currency_id.id,
                "company_currency_id": self.company_id.currency_id.id,
                "journal_id": self.id,
                "move_id": move.id,
                "date": move.date,
                "balance": values["debit"] - values["credit"],
                "amount_residual_currency": 0,
                "user_type_id": account.user_type_id.id,
                "reconciled": False,
            }
        )
        values = move_line_obj._add_missing_default_values(values)
        return values

    def prepare_move_vals(self, result_row_list, parser):
        """Hook to build the values of the statement from the parser and
        the profile.
        """
        vals = {
            "journal_id": self.id,
            "currency_id": self.currency_id.id,
            "import_partner_id": self.partner_id.id,
        }
        vals.update(parser.get_move_vals())
        return vals

    def multi_move_import(self, file_stream, ftype="csv"):
        """Create multiple bank statements from values given by the parser for
        the given profile.

        :param int/long profile_id: ID of the profile used to import the file
        :param filebuffer file_stream: binary of the provided file
        :param char: ftype represent the file extension (csv by default)
        :return: list: list of ids of the created account.bank.statement
        """
        filename = self._context.get("file_name", None)
        if filename:
            (filename, __) = os.path.splitext(filename)
        parser = new_move_parser(self, ftype=ftype, move_ref=filename)
        res = self.env["account.move"]
        for result_row_list in parser.parse(file_stream):
            move = self._move_import(
                parser,
                file_stream,
                result_row_list=result_row_list,
                ftype=ftype,
            )
            res |= move
        return res

    def _move_import(
            self, parser, file_stream, result_row_list=None, ftype="csv"):
        """Create a bank statement with the given profile and parser. It will
        fulfill the bank statement with the values of the file provided, but
        will not complete data (like finding the partner, or the right
        account). This will be done in a second step with the completion rules.

        :param prof : The profile used to import the file
        :param parser: the parser
        :param filebuffer file_stream: binary of the provided file
        :param char: ftype represent the file extension (csv by default)
        :return: ID of the created account.bank.statement
        """
        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]
        attachment_obj = self.env["ir.attachment"]
        if result_row_list is None:
            result_row_list = parser.result_row_list
        # Check all key are present in account.bank.statement.line!!
        if not result_row_list:
            raise UserError(_("Nothing to import: " "The file is empty"))
        parsed_cols = list(
            parser.get_move_line_vals(result_row_list[0]).keys()
        )
        for col in parsed_cols:
            if col not in move_line_obj._fields:
                raise UserError(
                    _(
                        "Missing column! Column %s you try to import is not "
                        "present in the move line!"
                    )
                    % col
                )
        move_vals = self.prepare_move_vals(result_row_list, parser)
        move = move_obj.create(move_vals)
        try:
            # Record every line in the bank statement
            move_store = []
            for line in result_row_list:
                parser_vals = parser.get_move_line_vals(line)
                values = self.prepare_move_line_vals(parser_vals, move)
                move_store.append(values)
            move_line_obj.with_context(check_move_validity=False).create(
                move_store
            )
            self._write_extra_move_lines(parser, move)
            if self.create_counterpart:
                self._create_counterpart(parser, move)
            # Check if move is balanced
            move.assert_balanced()
            # Computed total amount of the move
            move._amount_compute()
            # Attach data to the move
            attachment_data = {
                "name": "statement file",
                "datas": file_stream,
                "datas_fname": "%s.%s" % (fields.Date.today(), ftype),
                "res_model": "account.move",
                "res_id": move.id,
            }
            attachment_obj.create(attachment_data)
            # If user ask to launch completion at end of import, do it!
            if self.launch_import_completion:
                move.button_auto_completion()
            # Write the needed log infos on profile
            self.write_logs_after_import(move, len(result_row_list))
        except UserError:
            # "Clean" exception, raise as such
            raise
        except Exception:
            error_type, error_value, trbk = sys.exc_info()
            st = "Error: %s\nDescription: %s\nTraceback:" % (
                error_type.__name__,
                error_value,
            )
            st += "".join(traceback.format_tb(trbk, 30))
            raise ValidationError(
                _(
                    "Statement import error "
                    "The statement cannot be created: %s"
                )
                % st
            )
        return move
