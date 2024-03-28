# Copyright 2022 Akretion France - Alexis de Lattre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_bank_reconciliation_start = fields.Date(
        related="company_id.account_bank_reconciliation_start", readonly=False
    )
