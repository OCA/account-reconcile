# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone, Damien Crier
#    Copyright 2014, 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
