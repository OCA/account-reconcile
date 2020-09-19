# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def action_apply_postprocessing(self):
        self.mapped('line_ids').action_apply_postprocessing()
