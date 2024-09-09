from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def create_cash_statement(self):
        # Totally override this action for avoiding the standard
        # message saying that you need to install the enterprise
        # module. We do the equivalent thing instead.
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_statement_base.account_bank_statement_line_action"
        )
        action["context"] = {"search_default_journal_id": self.id}
        return action
