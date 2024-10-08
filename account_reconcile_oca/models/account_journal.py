# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    reconcile_mode = fields.Selection(
        [("edit", "Edit Move"), ("keep", "Keep Suspense Accounts")],
        default="edit",
        required=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency"
    )
    reconcile_aggregate = fields.Selection(
        [
            ("statement", "Statement"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
        ],
        string="Reconcile aggregation",
        help="Aggregation to use on reconcile view",
    )

    def get_rainbowman_message(self):
        self.ensure_one()
        if self.get_journal_dashboard_datas()["number_to_reconcile"] > 0:
            return False
        return _("Well done! Everything has been reconciled")

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        """Populate all bank and cash journal's data dict with
        relevant information for the kanban card."""
        super()._fill_bank_cash_dashboard_data(dashboard_data)
        bank_cash_journals = self.filtered(
            lambda journal: journal.type in ("bank", "cash")
        )
        if not bank_cash_journals:
            return
        for journal in bank_cash_journals:
            dashboard_data[journal.id].update(
                {
                    "show_reconcile_button_with_no_entries_to_reconcile": (
                        journal.company_id.show_reconcile_button_with_no_entries_to_reconcile
                    )
                }
            )
