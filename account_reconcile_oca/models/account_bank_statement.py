# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountBankStatement(models.Model):
    _name = "account.bank.statement"
    _inherit = ["account.bank.statement", 'mail.thread', 'mail.activity.mixin']

    is_reconciled = fields.Boolean(string="Approved", compute='_compute_is_reconciled',
        store=True)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("confirmed", "Confirmed"),
        ],
        string="Status",
        tracking=True,
        default="open",
        readonly=True,
        help="The status is set to Open, when a statement is created.\n"
        "When the statement is approved , the status is set Confirmed.\n"
    )

    @api.depends('is_complete', 'line_ids.is_reconciled')
    def _compute_is_reconciled(self):
        for stmt in self:
            stmt.is_reconciled = (all(line.is_reconciled for line in stmt.line_ids)
                               and stmt.is_complete)

    def _compute_date_index(self):
        for stmt in self:
            sorted_lines = stmt.line_ids.filtered(lambda line: line._origin.id).sorted(
                'internal_index')
            stmt.first_line_index = sorted_lines[:1].internal_index
            stmt.date = sorted_lines.filtered(lambda l: l.state == 'posted')[-1:].date

    def action_open_statement(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_bank_statement_action_edit"
        )
        action["res_id"] = self.id
        return action

    def action_confirm_statement(self):
        for rec in self:
            if not rec.is_valid:
                raise ValidationError(_("Starting balance must match "
                                        "the ending balance of the previous statement."))
            if not rec.is_reconciled:
                raise ValidationError(_("All statement lines must be reconciled."))

            if not rec.is_complete:
                raise ValidationError(_("Sum of statement lines must equal to the "
                                        "difference between start and end balance"))

            rec.state = "confirmed"

    def unlink(self):
        for statement in self:
            statement.line_ids.unlink()
        return super(AccountBankStatement, self).unlink()



