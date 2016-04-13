# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Leonardo Pistone, Damien Crier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    reconciliation_commit_every = fields.Integer(
        related="company_id.reconciliation_commit_every",
        string="How often to commit when performing automatic "
        "reconciliation.",
        help="Leave zero to commit only at the end of the process."
    )

    @api.multi
    def onchange_company_id(self, company_id):

        result = super(AccountConfigSettings, self).onchange_company_id(
            company_id
        )

        if company_id:
            company = self.env['res.company'].browse(company_id)
            result['value']['reconciliation_commit_every'] = (
                company.reconciliation_commit_every
            )
        return result


class Company(models.Model):
    _inherit = "res.company"

    reconciliation_commit_every = fields.Integer(
        string="How often to commit when performing automatic "
        "reconciliation.",
        help="Leave zero to commit only at the end of the process."
    )
