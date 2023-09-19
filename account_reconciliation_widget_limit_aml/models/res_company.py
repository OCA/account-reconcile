# Copyright 2023 Valentin Vinagre <valentin.vinagre@sygel.es>
# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_bank_reconciliation_start_all_aml = fields.Boolean(
        string="Filter all account move lines"
    )
