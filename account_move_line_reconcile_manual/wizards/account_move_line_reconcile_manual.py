# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class AccountMoveLineReconcileManual(models.TransientModel):
    _name = "account.move.line.reconcile.manual"
    _description = "Manual Reconciliation Wizard"
    _check_company_auto = True

    account_id = fields.Many2one(
        "account.account", required=True, readonly=True, check_company=True
    )
    company_id = fields.Many2one("res.company", required=True, readonly=True)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    count = fields.Integer(string="# of Journal Items", readonly=True)
    total_debit = fields.Monetary(currency_field="company_currency_id", readonly=True)
    total_credit = fields.Monetary(currency_field="company_currency_id", readonly=True)
    move_line_ids = fields.Many2many(
        "account.move.line", readonly=True, check_company=True
    )
    partner_count = fields.Integer(readonly=True)
    partner_id = fields.Many2one("res.partner", readonly=True)
    state = fields.Selection(
        [
            ("start", "Start"),
            ("writeoff", "Write-off"),
        ],
        readonly=True,
        default="start",
    )
    # START WRITE-OFF FIELDS
    writeoff_model_id = fields.Many2one(
        "account.reconcile.manual.model",
        string="Model",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    writeoff_journal_id = fields.Many2one(
        "account.journal",
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Journal",
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        check_company=True,
    )
    writeoff_date = fields.Date(string="Date", default=fields.Date.context_today)
    writeoff_ref = fields.Char(
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Reference",
        default=lambda self: _("Write-off"),
    )
    writeoff_type = fields.Selection(
        [
            ("income", "Income"),
            ("expense", "Expense"),
            ("none", "None"),
        ],
        readonly=True,
        string="Type",
    )
    writeoff_amount = fields.Monetary(
        currency_field="company_currency_id", readonly=True, string="Amount"
    )
    writeoff_account_id = fields.Many2one(
        "account.account",
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Write-off Account",
        domain="[('company_id', '=', company_id), ('deprecated', '=', False)]",
        check_company=True,
    )
    writeoff_analytic_distribution = fields.Json(
        string="Analytic",
        compute="_compute_writeoff_analytic_distribution",
        readonly=False,
        store=True,
        precompute=True,
    )
    analytic_precision = fields.Integer(
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )

    @api.depends("writeoff_model_id")
    def _compute_writeoff(self):
        for wiz in self:
            if wiz.writeoff_model_id:
                model = wiz.writeoff_model_id
                wiz.writeoff_journal_id = model.journal_id
                wiz.writeoff_ref = model.ref
                if wiz.writeoff_type == "expense":
                    wiz.writeoff_account_id = model.expense_account_id.id
                    if model.expense_analytic_distribution:
                        wiz.writeoff_analytic_distribution = (
                            model.expense_analytic_distribution
                        )
                elif wiz.writeoff_type == "income":
                    wiz.writeoff_account_id = model.income_account_id.id
                    if model.income_analytic_distribution:
                        wiz.writeoff_analytic_distribution = (
                            model.income_analytic_distribution
                        )
            else:
                journals = self.env["account.journal"].search(
                    [("type", "=", "general"), ("company_id", "=", wiz.company_id.id)]
                )
                if len(journals) == 1:
                    wiz.writeoff_journal_id = journals.id

    @api.depends("writeoff_account_id")
    def _compute_writeoff_analytic_distribution(self):
        aadmo = self.env["account.analytic.distribution.model"]
        for wiz in self:
            if wiz.writeoff_account_id and not wiz.writeoff_analytic_distribution:
                wiz.writeoff_analytic_distribution = aadmo._get_distribution(
                    {
                        "account_prefix": wiz.writeoff_account_id.code,
                        "company_id": wiz.company_id.id,
                    }
                )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get("active_model") == self._name:  # write-off step
            return res
        assert self._context.get("active_model") == "account.move.line"
        move_lines = self.env["account.move.line"].browse(
            self._context.get("active_ids")
        )
        company = move_lines[0].account_id.company_id
        ccur = company.currency_id
        count = 0
        account = False
        total_debit = total_credit = 0.0
        partner_set = set()
        for line in move_lines:
            count += 1
            total_debit += line.debit
            total_credit += line.credit
            if line.full_reconcile_id:
                raise UserError(
                    _("Line '%s' is already fully reconciled.") % line.display_name
                )
            if account:
                if account != line.account_id:
                    raise UserError(
                        _(
                            "The Journal Items selected have different accounts: "
                            "%(account1)s and %(account2)s.",
                            account1=account.code,
                            account2=line.account_id.code,
                        )
                    )
            else:
                account = line.account_id
            if line.partner_id:
                partner_set.add(line.partner_id.id)
        # if lines have the same account, they are in the same company
        if not account.reconcile:
            raise UserError(
                _("Account '%s' is not reconciliable.") % account.display_name
            )
        if count <= 1:
            raise UserError(_("You must select at least 2 journal items!"))
        if ccur.is_zero(total_debit):
            raise UserError(_("You selected only credit journal items."))
        if ccur.is_zero(total_credit):
            raise UserError(_("You selected only debit journal items."))
        writeoff_amount = ccur.round(abs(total_debit - total_credit))
        total_debit = ccur.round(total_debit)
        total_credit = ccur.round(total_credit)
        compare_res = ccur.compare_amounts(total_debit, total_credit)
        if compare_res > 0:
            writeoff_type = "expense"
        elif compare_res < 0:
            writeoff_type = "income"
        else:
            writeoff_type = "none"
        res.update(
            {
                "count": count,
                "account_id": account.id,
                "company_id": account.company_id.id,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "partner_count": len(partner_set),
                "partner_id": len(partner_set) == 1 and partner_set.pop() or False,
                "move_line_ids": move_lines.ids,
                "writeoff_type": writeoff_type,
                "writeoff_amount": writeoff_amount,
            }
        )
        return res

    def full_reconcile(self):
        self.ensure_one()
        self.move_line_ids.remove_move_reconcile()
        res = self.move_line_ids.reconcile()
        if not res.get("full_reconcile"):
            raise UserError(_("Full reconciliation failed. It should never happen!"))
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Successful reconciliation"),
                "message": _("Reconcile mark: %s") % res["full_reconcile"].display_name,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return action

    def partial_reconcile(self):
        self.ensure_one()
        self.move_line_ids.remove_move_reconcile()
        self.move_line_ids.reconcile()
        return

    def go_to_writeoff(self):
        self.ensure_one()
        self.write({"state": "writeoff"})
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_move_line_reconcile_manual.account_move_line_reconcile_manual_action"
        )
        action["res_id"] = self.id
        return action

    def _prepare_writeoff_move(self):
        ccur = self.company_currency_id
        bal = ccur.round(self.total_debit - self.total_credit)
        compare_res = ccur.compare_amounts(bal, 0)
        assert compare_res
        if compare_res > 0:
            credit = bal
            debit = 0
        else:
            debit = bal * -1
            credit = 0
        vals = {
            "company_id": self.company_id.id,
            "journal_id": self.writeoff_journal_id.id,
            "ref": self.writeoff_ref,
            "date": self.writeoff_date,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "display_type": "payment_term",
                        "account_id": self.account_id.id,
                        "partner_id": self.partner_id and self.partner_id.id or False,
                        "debit": debit,
                        "credit": credit,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "display_type": "product",
                        "account_id": self.writeoff_account_id.id,
                        "partner_id": self.partner_id and self.partner_id.id or False,
                        "debit": credit,
                        "credit": debit,
                        "analytic_distribution": self.writeoff_analytic_distribution,
                    },
                ),
            ],
        }
        return vals

    def reconcile_with_writeoff(self):
        self.ensure_one()
        assert self.writeoff_journal_id
        assert self.writeoff_date
        assert self.writeoff_account_id
        assert self.state == "writeoff"
        self.move_line_ids.remove_move_reconcile()
        vals = self._prepare_writeoff_move()
        woff_move = self.env["account.move"].create(vals)
        woff_move.with_context(validate_analytic=True)._post(soft=False)
        to_rec_woff_line = woff_move.line_ids.filtered(
            lambda x: x.account_id.id == self.account_id.id
        )
        assert len(to_rec_woff_line) == 1
        to_rec_lines = self.move_line_ids + to_rec_woff_line
        res = to_rec_lines.reconcile()
        if not res.get("full_reconcile"):
            raise UserError(_("Full reconciliation failed. It should never happen!"))
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Successful reconciliation"),
                "message": _(
                    "Write-off journal entry: %(writeoff_move)s\nReconcile mark: %(full_rec)s",
                    full_rec=res["full_reconcile"].display_name,
                    writeoff_move=woff_move.name,
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return action

    @api.onchange("writeoff_account_id")
    def writeoff_account_id_change(self):
        account = self.writeoff_account_id
        if (
            self.writeoff_type in ("income", "expense")
            and account
            and self.writeoff_type not in account.account_type
        ):
            message = _(
                "This is a/an '%(writeoff_type)s' write-off, "
                "but you selected account %(account_code)s "
                "which is a/an '%(account_type)s' account.",
                writeoff_type=self._fields["writeoff_type"].convert_to_export(
                    self.writeoff_type, self
                ),
                account_code=account.code,
                account_type=account._fields["account_type"].convert_to_export(
                    account.account_type, account
                ),
            )
            res = {
                "warning": {
                    "title": _("Bad write-off account type"),
                    "message": message,
                }
            }
            return res
