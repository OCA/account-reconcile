# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    restrict_partner_mismatch_on_reconcile = fields.Boolean(
        related="company_id.restrict_partner_mismatch_on_reconcile",
        readonly=False,
    )
