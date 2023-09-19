# Copyright 2023 Valentin Vinagre <valentin.vinagre@sygel.es>
# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_bank_reconciliation_start_all_aml = fields.Boolean(
        related="company_id.account_bank_reconciliation_start_all_aml", readonly=False
    )
