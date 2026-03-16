# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    no_restrict_partner_mismatch_on_reconcile = fields.Boolean(
        help="Check this if you don't want to restrict partner "
        "mismatch (several differents) on reconcile."
    )
