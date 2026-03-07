# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


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

    @api.model
    def get_rainbowman_message(self, journal_id=None):
        """
        Check if all bank statement lines for a journal are reconciled.
        Returns a message if complete, False otherwise.

        v19 changed RPC call binding - using @api.model with explicit journal_id param
        instead of relying on recordset binding which was unreliable.
        """
        _logger.info(
            "get_rainbowman_message called with journal_id=%s (type: %s)",
            journal_id,
            type(journal_id).__name__,
        )
        if not journal_id:
            _logger.warning("get_rainbowman_message: No journal_id provided")
            return False

        # Get journal for logging
        journal = self.browse(journal_id)

        # Count unreconciled bank statement lines directly instead of relying on
        # dashboard data structure which changed in v19
        unreconciled_count = self.env["account.bank.statement.line"].search_count(
            [
                ("journal_id", "=", journal_id),
                ("is_reconciled", "=", False),
            ]
        )
        _logger.info(
            "Rainbowman check for journal %s (ID %s): %s unreconciled lines",
            journal.name,
            journal_id,
            unreconciled_count,
        )
        if unreconciled_count > 0:
            return False
        return _("Well done! Everything has been reconciled")

    def open_action(self):
        """
        Return OCA *Reconcile All* when core *Bank Statements* tree is requested;
        leave other actions unchanged.
        """
        action = super().open_action()
        if action.get("xml_id") == "account.action_bank_statement_tree":
            action = self.env["ir.actions.actions"]._for_xml_id(
                "account_reconcile_oca.action_bank_statement_line_reconcile_all"
            )
        return action
