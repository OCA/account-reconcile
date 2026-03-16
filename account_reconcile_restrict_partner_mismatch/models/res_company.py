# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    restrict_partner_mismatch_on_reconcile = fields.Boolean(
        help="Check this if you want to avoid partner mismatch"
        " (several different partners) on reconciliation."
    )
