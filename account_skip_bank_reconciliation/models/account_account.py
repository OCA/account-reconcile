# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    exclude_bank_reconcile = fields.Boolean(
        string="Exclude from Bank Reconciliation",
        default=False,
        help="Check this box if the journal items of this account "
        "should not appear in the list of journal items to match "
        "a statement line.",
    )
