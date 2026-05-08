# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount


class AccountManualReconcileWizard(models.TransientModel):
    _name = "account.manual.reconcile.wizard"
    _description = "Manual Reconciliation Wizard"
    _check_company_auto = True

    move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Move Lines to Reconcile",
        readonly=True,
    )
    reconciliation_account_id = fields.Many2one(
        "account.account",
        compute="_compute_wizard_data",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        compute="_compute_wizard_data",
        store=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency", compute="_compute_wizard_data", store=True
    )
    balance_difference = fields.Monetary(
        compute="_compute_wizard_data",
        currency_field="company_currency_id",
        store=True,
    )
    need_transfer = fields.Boolean(
        compute="_compute_wizard_data",
        store=True,
    )
    need_write_off = fields.Boolean(
        compute="_compute_wizard_data",
        store=True,
    )
    allow_partial_reconcile = fields.Boolean(
        compute="_compute_allow_partial_reconcile",
        store=True,
        readonly=False,
        help="Allow reconciliation even if balances do not match exactly",
    )
    display_allow_partial_reconcile = fields.Boolean(
        compute="_compute_wizard_data",
        store=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        check_company=True,
        domain="[('type', '=', 'general')]",
        compute="_compute_journal_id",
        store=True,
        readonly=False,
    )
    date = fields.Date(default=fields.Date.context_today)
    reference = fields.Char()
    write_off_line_ids = fields.One2many(
        "account.manual.reconcile.wizard.line",
        "wizard_id",
        help="Add lines for write-offs, adjustments, counterparts, etc.",
    )
    write_off_amount = fields.Float(compute="_compute_write_off_amount")

    reconcile_model_id = fields.Many2one(
        "account.reconcile.model",
        domain=[
            ("rule_type", "=", "writeoff_button"),
            ("counterpart_type", "=", "general"),
        ],
        help="Select a reconciliation model to auto-load lines",
    )

    @api.depends("move_line_ids")
    def _compute_allow_partial_reconcile(self):
        for wizard in self:
            wizard.allow_partial_reconcile = len(wizard.move_line_ids) > 1

    @api.depends("move_line_ids", "allow_partial_reconcile")
    def _compute_wizard_data(self):
        for wizard in self:
            lines = wizard.move_line_ids
            company = lines.company_id
            currency = company.currency_id
            wizard.company_id = company
            wizard.company_currency_id = currency
            total_debit = total_credit = 0.0
            amounts_by_account = defaultdict(float)
            accounts = lines.account_id
            for line in lines:
                total_debit += line.amount_residual if line.debit > 0 else 0.0
                total_credit += line.amount_residual if line.credit > 0 else 0.0
                amounts_by_account[line.account_id] += line.amount_residual
            reconciliation_account_id = accounts[0]
            need_transfer = False
            if len(accounts) == 2:
                need_transfer = True
                if abs(amounts_by_account[accounts[1]]) > abs(
                    amounts_by_account[accounts[0]]
                ):
                    reconciliation_account_id = accounts[1]
            wizard.reconciliation_account_id = reconciliation_account_id
            wizard.balance_difference = total_debit + total_credit
            wizard.need_transfer = need_transfer
            wizard.need_write_off = not currency.is_zero(wizard.balance_difference)
            wizard.display_allow_partial_reconcile = total_debit and total_credit

    @api.depends("company_id")
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env["account.journal"].search(
                [
                    *self.env["account.journal"]._check_company_domain(
                        wizard.company_id
                    ),
                    ("type", "=", "general"),
                ],
                limit=1,
            )

    @api.depends(
        "write_off_line_ids", "write_off_line_ids.debit", "write_off_line_ids.credit"
    )
    def _compute_write_off_amount(self):
        for wizard in self:
            wizard.write_off_amount = sum(
                line.debit - line.credit for line in wizard.write_off_line_ids
            )

    @api.onchange("reconcile_model_id")
    def _onchange_reconcile_model_id(self):
        if self.reconcile_model_id:
            self.write_off_line_ids = [Command.clear()]
            line_vals = []
            balance_amount = self.balance_difference
            for model_line in self.reconcile_model_id.line_ids:
                if model_line.amount_type == "fixed":
                    amount = model_line.amount
                elif model_line.amount_type in ["percentage", "percentage_st_line"]:
                    amount = balance_amount * model_line.amount * 0.01
                if self.company_currency_id.is_zero(amount):
                    continue
                line_vals.append(
                    Command.create(
                        {
                            "name": model_line.label or self.env._("Write-Off"),
                            "account_id": model_line.account_id.id,
                            "credit": amount if amount > 0 else 0.0,
                            "debit": -amount if amount < 0 else 0.0,
                            "analytic_distribution": model_line.analytic_distribution,
                        },
                    )
                )
            self.write_off_line_ids = line_vals

    @api.model
    def _check_move_lines(self, move_lines):
        companies = move_lines.company_id
        if len(companies) > 1:
            raise UserError(
                self.env._("All selected lines must be from the same company.")
            )
        reconciled_lines = move_lines.filtered("reconciled")
        if reconciled_lines:
            raise UserError(self.env._("Cannot reconcile already reconciled lines."))
        if len(move_lines.account_id) > 2:
            raise UserError(
                self.env._(
                    "You can only reconcile entries from up to 2 different accounts."
                )
            )
        if len(move_lines.partner_id) > 1:
            raise UserError(
                self.env._("You can only reconcile entries from the same partner.")
            )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Get selected move lines from context
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model")
        if (
            "move_line_ids" in fields_list
            and active_model == "account.move.line"
            and active_ids
        ):
            move_lines = self.env["account.move.line"].browse(active_ids)
            self._check_move_lines(move_lines)
            res["move_line_ids"] = [Command.set(move_lines.ids)]
        return res

    def _prepare_account_move_vals(self):
        return {
            "journal_id": self.journal_id.id,
            "date": self.date,
            "ref": self.reference,
            "company_id": self.company_id.id,
            "move_type": "entry",
        }

    def _prepare_transfer_lines(self):
        lines_to_transfer = self.move_line_ids.filtered(
            lambda line: line.account_id != self.reconciliation_account_id
        )
        from_account = self.move_line_ids.account_id - self.reconciliation_account_id
        amount = sum(line.amount_residual for line in lines_to_transfer)
        partner = self.move_line_ids.partner_id
        line_vals = [
            Command.create(
                {
                    "name": self.env._(
                        "Transfer to %s",
                        self.reconciliation_account_id.display_name,
                    ),
                    "account_id": from_account.id,
                    "partner_id": partner.id,
                    "balance": -amount,
                }
            ),
            Command.create(
                {
                    "name": self.env._("Transfer from %s", from_account.display_name),
                    "account_id": self.reconciliation_account_id.id,
                    "partner_id": partner.id,
                    "balance": amount,
                }
            ),
        ]
        return line_vals

    def _prepare_write_off_lines(self):
        partner = self.move_line_ids.partner_id
        line_values = [
            Command.create(
                {
                    "name": self.env._("Write-Off"),
                    "account_id": self.reconciliation_account_id.id,
                    "partner_id": partner.id,
                    "balance": -self.balance_difference,
                }
            )
        ]
        for line in self.write_off_line_ids:
            balance = line.debit - line.credit
            line_values.append(
                Command.create(
                    {
                        "name": line.name or self.env._("Write-Off"),
                        "account_id": line.account_id.id,
                        "partner_id": partner.id,
                        "analytic_distribution": line.analytic_distribution,
                        "balance": -balance,
                    }
                )
            )
        return line_values

    def create_account_move(self, line_values):
        self.ensure_one()
        move_vals = self._prepare_account_move_vals()
        move_vals.update({"line_ids": line_values})
        account_move = (
            self.env["account.move"]
            .with_context(
                skip_invoice_sync=True,
                skip_invoice_line_sync=True,
            )
            .create(move_vals)
        )
        account_move.action_post()
        return account_move

    def _validate_reconciliation(self):
        total_write_off = sum(
            line.debit - line.credit for line in self.write_off_line_ids
        )
        if not self.company_currency_id.is_zero(
            total_write_off + self.balance_difference
        ):
            amount_str = format_amount(
                self.env, self.balance_difference, self.company_currency_id
            )
            raise UserError(
                self.env._(
                    "The total of write-off lines must balance the difference of %s.",
                    amount_str,
                )
            )

    def _action_reconcile(self):
        if self.need_write_off and not self.allow_partial_reconcile:
            self._validate_reconciliation()
        lines_to_reconcile = self.move_line_ids
        new_move_lines = []
        if self.need_transfer:
            new_move_lines.extend(self._prepare_transfer_lines())
        if self.need_write_off and not self.allow_partial_reconcile:
            new_move_lines.extend(self._prepare_write_off_lines())
        if new_move_lines:
            account_move = self.create_account_move(new_move_lines)
            lines_to_reconcile += account_move.line_ids
        lines_by_account = lines_to_reconcile.grouped("account_id")
        for account, lines in lines_by_account.items():
            if account.reconcile:
                self.env["account.move.line"]._reconcile_plan([lines])
        return lines_to_reconcile

    def _get_action(self):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Success"),
                "message": self.env._(
                    "The selected lines have been successfully reconciled."
                ),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_reconcile(self):
        self._action_reconcile()
        return self._get_action()

    def action_reconcile_and_open(self):
        action = self._get_action()
        move_lines_reconciled = self._action_reconcile()
        if move_lines_reconciled:
            action["params"]["next"] = move_lines_reconciled.open_reconcile_view()
        return action


class AccountManualReconcileWizardLine(models.TransientModel):
    _inherit = "analytic.mixin"
    _name = "account.manual.reconcile.wizard.line"
    _description = "Account Manual Reconcile Line"
    _check_company_auto = True

    wizard_id = fields.Many2one("account.manual.reconcile.wizard", ondelete="cascade")
    company_id = fields.Many2one(related="wizard_id.company_id")
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Currency"
    )
    name = fields.Char(
        string="Description", default=lambda self: self.env._("Write-Off")
    )
    account_id = fields.Many2one(
        "account.account",
        required=True,
        check_company=True,
        domain="[('deprecated', '=', False), ('account_type', '!=', 'off_balance')]",
    )
    debit = fields.Monetary(
        compute="_compute_debit",
        currency_field="company_currency_id",
        store=True,
        readonly=False,
    )
    credit = fields.Monetary(
        compute="_compute_credit",
        currency_field="company_currency_id",
        store=True,
        readonly=False,
    )

    @api.depends("wizard_id")
    def _compute_debit(self):
        for line in self:
            if line.wizard_id.balance_difference < 0 and not line.debit:
                line.debit = (
                    -line.wizard_id.balance_difference - line.wizard_id.write_off_amount
                )

    @api.depends("wizard_id")
    def _compute_credit(self):
        for line in self:
            if line.wizard_id.balance_difference > 0 and not line.credit:
                line.credit = (
                    line.wizard_id.balance_difference + line.wizard_id.write_off_amount
                )

    @api.onchange("debit")
    def _onchange_debit(self):
        for line in self:
            if line.debit:
                line.credit = 0

    @api.onchange("credit")
    def _onchange_credit(self):
        for line in self:
            if line.credit:
                line.debit = 0

    @api.constrains("debit", "credit")
    def _check_debit_credit(self):
        for line in self:
            if line.debit < 0 or line.credit < 0:
                raise UserError(
                    self.env._("Debit and credit amounts must be positive.")
                )
