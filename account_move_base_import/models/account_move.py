# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging
import sys
import traceback

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ErrorTooManyPartner(Exception):
    """New Exception definition that is raised when more than one partner is
    matched by the completion rule.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return repr(self.value)


class AccountMoveCompletionRule(models.Model):
    """This will represent all the completion method that we can have to
    fulfill the bank statement lines. You'll be able to extend them in you own
    module and choose those to apply for every statement profile.
    The goal of a rule is to fulfill at least the partner of the line, but
    if possible also the reference because we'll use it in the reconciliation
    process. The reference should contain the invoice number or the SO number
    or any reference that will be matched by the invoice accounting move.
    """

    _name = "account.move.completion.rule"
    _order = "sequence asc"
    _description = "Account move completion method"

    sequence = fields.Integer(string="Sequence", help="Lower means parsed first.")
    name = fields.Char(string="Name")
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="account_journal_completion_rule_rel",
        string="Related journals",
    )
    function_to_call = fields.Selection(
        [
            (
                "get_from_name_and_invoice",
                "From line name (based on customer invoice number)",
            ),
            (
                "get_from_name_and_supplier_invoice",
                "From line name (based on supplier invoice number)",
            ),
            (
                "get_from_name_and_partner_field",
                "From line name (based on partner field)",
            ),
            (
                "get_from_name_and_partner_name",
                "From line name (based on partner name)",
            ),
        ],
        string="Method",
    )

    def _find_invoice(self, line, inv_type):
        """Find invoice related to statement line"""
        inv_obj = self.env["account.move"]
        if inv_type == "supplier":
            type_domain = ("in_invoice", "in_refund")
            number_field = "ref"
        elif inv_type == "customer":
            type_domain = ("out_invoice", "out_refund")
            number_field = "name"
        else:
            raise ValidationError(
                _("Invalid invoice type for completion: %s") % inv_type
            )

        invoices = inv_obj.search(
            [(number_field, "=", line.name.strip()), ("move_type", "in", type_domain)]
        )
        if invoices:
            if len(invoices) == 1:
                return invoices
            else:
                raise ErrorTooManyPartner(
                    _(
                        'Line named "%s" was matched by more than one '
                        "partner while looking on %s invoices"
                    )
                    % (line.name, inv_type)
                )
        return False

    def _from_invoice(self, line, inv_type):
        """Populate statement line values"""
        if inv_type not in ("supplier", "customer"):
            raise ValidationError(
                _("Invalid invoice type for completion: %s") % inv_type
            )
        res = {}
        invoice = self._find_invoice(line, inv_type)
        if invoice:
            partner_id = invoice.commercial_partner_id.id
            res = {"partner_id": partner_id}
        return res

    # Should be private but data are initialised with no update XML
    def get_from_name_and_supplier_invoice(self, line):
        """Match the partner based on the invoice number and the reference of
        the statement line. Then, call the generic get_values_for_line method
        to complete other values. If more than one partner matched, raise the
        ErrorTooManyPartner error.

        :param dict line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,
            ...}
        """
        return self._from_invoice(line, "supplier")

    # Should be private but data are initialised with no update XML
    def get_from_name_and_invoice(self, line):
        """Match the partner based on the invoice number and the reference of
        the statement line. Then, call the generic get_values_for_line method
        to complete other values. If more than one partner matched, raise the
        ErrorTooManyPartner error.

        :param dict line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,
            ...}
        """
        return self._from_invoice(line, "customer")

    # Should be private but data are initialised with no update XML
    def get_from_name_and_partner_field(self, line):
        """
        Match the partner based on the label field of the statement line and
        the text defined in the 'bank_statement_label' field of the partner.
        Remember that we can have values separated with ; Then, call the
        generic get_values_for_line method to complete other values.  If more
        than one partner matched, raise the ErrorTooManyPartner error.

        :param dict line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        res = {}
        partner_obj = self.env["res.partner"]
        or_regex = ".*;? *%s *;?.*" % line.name
        self.env["res.partner"].flush(["bank_statement_label"])
        sql = "SELECT id from res_partner" " WHERE bank_statement_label ~* %s"
        self.env.cr.execute(sql, (or_regex,))
        partner_ids = self.env.cr.fetchall()
        partners = partner_obj.browse([x[0] for x in partner_ids])
        if partners:
            if len(partners) > 1:
                msg = _(
                    'Line named "%s" was matched by more than '
                    "one partner while looking on partner label: %s"
                ) % (line.name, ",".join([x.name for x in partners]))
                raise ErrorTooManyPartner(msg)
            res["partner_id"] = partners[0].id
        return res

    def get_from_name_and_partner_name(self, line):
        """Match the partner based on the label field of the statement line and
        the name of the partner. Then, call the generic get_values_for_line
        method to complete other values. If more than one partner matched,
        raise the ErrorTooManyPartner error.

        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        res = {}
        # The regexp_replace() escapes the name to avoid false positive
        # example: 'John J. Doe (No 1)' is escaped to 'John J\. Doe \(No 1\)'
        # See http://stackoverflow.com/a/400316/1504003 for a list of
        # chars to escape. Postgres is POSIX-ARE, compatible with
        # POSIX-ERE excepted that '\' must be escaped inside brackets according
        # to:
        #  http://www.postgresql.org/docs/9.0/static/functions-matching.html
        # in chapter 9.7.3.6. Limits and Compatibility
        self.env["res.partner"].flush(["name"])
        sql = r"""
        SELECT id FROM (
            SELECT id,
                regexp_matches(%s,
                    regexp_replace(name,'([\.\^\$\*\+\?\(\)\[\{\\\|])', %s,
                        'g'), 'i') AS name_match
            FROM res_partner)
            AS res_partner_matcher
        WHERE name_match IS NOT NULL"""
        self.env.cr.execute(sql, (line.name, r"\\\1"))
        result = self.env.cr.fetchall()
        if result:
            if len(result) > 1:
                raise ErrorTooManyPartner(
                    _(
                        'Line named "%s" was matched by more than one '
                        "partner while looking on partner by name"
                    )
                    % line.name
                )
            res["partner_id"] = result[0][0]
        return res


class AccountMoveLine(models.Model):
    """
    Add sparse field on the statement line to allow to store all the bank infos
    that are given by a bank/office. You can then add you own in your module.
    The idea here is to store all bank/office infos in the
    additional_bank_fields serialized field when importing the file. If many
    values, add a tab in the bank statement line to store your specific one.
    Have a look in account_move_base_import module to see how we've done
    it.
    """

    _inherit = "account.move.line"
    _order = "already_completed desc, date asc"

    already_completed = fields.Boolean(
        string="Auto-Completed",
        default=False,
        help="When this checkbox is ticked, the auto-completion "
        "process/button will ignore this line.",
    )

    def _get_line_values_from_rules(self):
        """We'll try to find out the values related to the line based on rules
        set on the profile.. We will ignore line for which already_completed
        is ticked.

        :return:
            A dict of dict value that can be passed directly to the write
            method of the move line or {}. The first dict has statement
            line ID as a key: {117009: {'partner_id': 100997,
            'account_id': 489L}}
        """
        self.ensure_one()
        vals = {}
        if not self.already_completed:
            # Ask the rule
            vals = self._find_values_from_rules()
        return vals

    def _find_values_from_rules(self):
        """This method will execute all related rules, in their sequence order,
        to retrieve all the values returned by the first rules that will match.
        :return:
            A dict of value that can be passed directly to the write method of
            the move line or {}
           {'partner_id': value,
            'account_id: value,
            ...}
        """
        self.ensure_one()
        rules = self.journal_id.rule_ids
        for rule in rules:
            method_to_call = getattr(
                self.env["account.move.completion.rule"], rule.function_to_call
            )
            result = method_to_call(self)
            if result:
                result["already_completed"] = True
                return result
        return None


class AccountMove(models.Model):
    """We add a basic button and stuff to support the auto-completion
    of the bank statement once line have been imported or manually fulfill.
    """

    _name = "account.move"
    _inherit = ["account.move", "mail.thread"]

    used_for_completion = fields.Boolean(
        related="journal_id.used_for_completion", readonly=True
    )
    completion_logs = fields.Text(string="Completion Log", readonly=True)
    import_partner_id = fields.Many2one("res.partner", string="Partner from import")

    @api.depends("line_ids.partner_id", "import_partner_id")
    def _compute_partner_id(self):
        for move in self:
            if move.import_partner_id:
                move.partner_id = move.import_partner_id
            else:
                super(AccountMove, move)._compute_partner_id()

    def write_completion_log(self, error_msg, number_imported):
        """Write the log in the completion_logs field of the bank statement to
        let the user know what have been done. This is an append mode, so we
        don't overwrite what already recoded.

        :param int/long stat_id: ID of the account.bank.statement
        :param char error_msg: Message to add
        :number_imported int/long: Number of lines that have been completed
        :return True
        """
        user_name = self.env.user.name
        number_line = len(self.line_ids)
        log = self.completion_logs or ""
        completion_date = fields.Datetime.now()
        message = _(
            "%s Account Move %s has %s/%s lines completed by " "%s \n%s\n%s\n"
        ) % (
            completion_date,
            self.name,
            number_imported,
            number_line,
            user_name,
            error_msg,
            log,
        )
        self.write({"completion_logs": message})

        body = (
            (
                _("Statement ID %s auto-completed for %s/%s lines completed")
                % (self.name, number_imported, number_line)
            ),
        )
        self.message_post(body=body)
        return True

    def button_auto_completion(self):
        """Complete line with values given by rules and tic the
        already_completed checkbox so we won't compute them again unless the
        user untick them!
        """
        compl_lines = 0
        for move in self:
            msg_lines = []
            res = False
            for line in move.line_ids:
                try:
                    res = line._get_line_values_from_rules()
                    if res:
                        compl_lines += 1
                except ErrorTooManyPartner as exc:
                    msg_lines.append(repr(exc))
                except Exception as exc:
                    msg_lines.append(repr(exc))
                    error_type, error_value, trbk = sys.exc_info()
                    st = "Error: {}\nDescription: {}\nTraceback:".format(
                        error_type.__name__,
                        error_value,
                    )
                    st += "".join(traceback.format_tb(trbk, 30))
                    _logger.error(st)
                if res:
                    try:
                        line.write(res)
                    except Exception as exc:
                        msg_lines.append(repr(exc))
                        error_type, error_value, trbk = sys.exc_info()
                        st = "Error: {}\nDescription: {}\nTraceback:".format(
                            error_type.__name__,
                            error_value,
                        )
                        st += "".join(traceback.format_tb(trbk, 30))
                        _logger.error(st)
            msg = "\n".join(msg_lines)
            move.write_completion_log(msg, compl_lines)
            if move.journal_id.autovalidate_completed_move and all(
                [line.already_completed for line in move.line_ids]
            ):
                move._post()
        return True
