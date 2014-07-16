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

from openerp.osv import orm, fields


class AccountConfigSettings(orm.TransientModel):
    _inherit = 'account.config.settings'

    _columns = {
        'reconciliation_commit_every': fields.related(
            'company_id',
            'reconciliation_commit_every',
            type='integer',
            string='How often to commit when performing automatic '
            'reconciliation.',
            help="""Leave zero to commit only at the end of the process."""),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        company_obj = self.pool['res.company']

        result = super(AccountConfigSettings, self).onchange_company_id(
            cr, uid, ids, company_id, context=None)

        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            result['value']['reconciliation_commit_every'] = (
                company.reconciliation_commit_every
            )
        return result


class Company(orm.Model):
    _inherit = "res.company"
    _columns = {
        'reconciliation_commit_every': fields.integer(
            string='How often to commit when performing automatic '
            'reconciliation.',
            help="""Leave zero to commit only at the end of the process."""),
    }
