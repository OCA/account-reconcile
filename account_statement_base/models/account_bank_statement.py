from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def action_open_statement_lines(self):
        self.ensure_one()
        if not self:
            return {}
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_statement_base.account_bank_statement_line_action"
        )
        action.update({"domain": [("statement_id", "=", self.id)]})
        return action
