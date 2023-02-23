from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    skip_remove_reconciliation = fields.Boolean(
        related="journal_id.skip_remove_reconciliation"
    )

    def button_draft(self):
        self = self.with_context(
            skip_remove_reconciliation=self.skip_remove_reconciliation
        )
        return super().button_draft()
