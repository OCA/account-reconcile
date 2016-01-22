# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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

from openerp import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    reconciliation_commit_every = fields.Integer(
            related='company_id.reconciliation_commit_every')

    @api.one
    @api.depends('company_id')
    def _company_onchange(self):
        self.reconciliation_commit_every = \
            self.company_id.reconciliation_commit_every


class Company(models.Model):
    _inherit = "res.company"

    reconciliation_commit_every = fields.Integer(
            string='How often to commit when performing automatic '
            'reconciliation.',
            help="""Leave zero to commit only at the end of the process.""")
