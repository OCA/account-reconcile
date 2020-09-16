# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    account_reconciliation_ids = fields.Many2many(
        relation="account_reconcile_account_journal_rel",
        comodel_name="account.account",
        string="Accounts to consider in reconciliation",
        domain=[("reconcile", "=", True)],
        help="If you enter accounts here they will be the only ones"
        "to be considered during the reconciliation",
    )
