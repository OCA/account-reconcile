# -*- coding: utf-8 -*-
##############################################################################
#
#    account_statement_sale_order for OpenERP
#    Copyright (C) 2013-14 Akretion Chafique DELLI <chafique.delli@akretion.com>
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

from openerp.tools.translate import _
from openerp.osv import orm, fields


class AccountStatementLine(orm.Model):
    _inherit = "account.bank.statement.line"

    _columns = {
        'sale_ids': fields.many2many('sale.order', string='Sale Orders',)

    }

    def _update_line(self, cr, uid, vals, context=None):
        if 'sale_ids' in vals:
            line_id = vals.pop('id')
            self.write(cr, uid, line_id, vals, context=context)
        else:
            super(AccountStatementLine, self)._update_line(
                cr, uid, vals, context=context)

    def onchange_sale_ids(self, cr, uid, ids, sale_ids, context=None):
        """
        Override of the basic method as we need to pass the profile_id
        in the on_change_type call.
        Moreover, we now call the get_account_and_type_for_counterpart method
        now to get the type to use.
        """
        if sale_ids and sale_ids[0][2]:
            sale_obj = self.pool['sale.order']
            sale_ids = sale_ids[0][2]
            sale = sale_obj.browse(cr, uid, sale_ids[0], context=context)
            res = self.onchange_partner_id(
                cr, uid, ids, sale.partner_id.id, context=context)
            res['value'].update({'partner_id': sale.partner_id.id})
            return res
        return {}

    def _check_partner_id(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            for sale_id in line.sale_ids:
                if sale_id.partner_id != line.sale_ids[0].partner_id:
                    raise orm.except_orm(_('Error on the line %s !') % line.id,
                                         _('The sale orders chosen have '
                                           'to belong to the same partner'))
        return True

    _constraints = [
        (_check_partner_id,
         'The sale orders chosen have to belong to the same partner',
         ['sale_ids']),
    ]


class AccountBankStatement(orm.Model):
    _inherit = "account.bank.statement"

    def _prepare_counterpart_move_line(self, *args, **kwargs):
        context = kwargs.get('context')
        if context is None:
            ctx = {}
        else:
            ctx = context.copy()
        ctx['countrepart'] = True
        kwargs['context'] = ctx
        return super(AccountBankStatement, self)._prepare_counterpart_move_line(*args, **kwargs)

    def _prepare_move_line_vals(self, cr, uid, st_line, *args, **kwargs):
        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            cr, uid, st_line, *args, **kwargs)
        if not kwargs.get('context', {}).get('countrepart'):
            res['sale_ids'] = [(6, 0, [sale.id for sale in st_line.sale_ids])]
        return res
