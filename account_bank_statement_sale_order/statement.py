# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-14 Akretion (<http://www.akretion.com>).
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

from openerp import models, api, fields, _
from openerp.exceptions import Warning


class AccountStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    sale_ids = fields.Many2many('sale.order', string='Sale Orders')

    @api.model
    def _update_line(self, vals):
        if 'sale_ids' in vals:
            line_id = vals.pop('id')
            self.write(line_id, vals)
        else:
            super(AccountStatementLine, self)._update_line(vals)

    @api.onchange('sale_ids')
    def onchange_sale_ids(self):
        """
        Override of the basic method as we need to pass the profile_id
        in the on_change_type call.
        Moreover, we now call the get_account_and_type_for_counterpart method
        now to get the type to use.
        """
        if self.sale_ids and self.sale_ids[0][2]:
            sale_obj = self.env['sale.order']
            sale_ids = self.sale_ids[0][2]
            sale = sale_obj.browse(sale_ids[0])
            res = self.onchange_partner_id(sale.partner_id.id)
            res['value'].update({'partner_id': sale.partner_id.id})
            return res
        return {}

    @api.multi
    @api.constrains('sale_ids')
    def _check_partner_id(self):
        for line in self:
            for sale_id in line.sale_ids:
                if sale_id.partner_id != line.sale_ids[0].partner_id:
                    raise Warning(_('Error on the line %s !') % line.id,
                                  _('The sale orders chosen have to belong '
                                    'to the same partner'))
        return True

    @api.model
    def process_reconciliation(self, mv_line_dicts, *args, **kwargs):
        if not kwargs.get('context', {}).get('balance_check'):
            self._context = kwargs.get('context')
            mv_line_dicts[0]['sale_ids'] = [
                (6, 0, [sale.id for sale in self.sale_ids])
            ]
        super(AccountStatementLine, self).process_reconciliation(mv_line_dicts)


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def balance_check(self, *args, **kwargs):
        self._context = kwargs.get('context')
        if self._context is None:
            ctx = {}
        else:
            ctx = self._context.copy()
        ctx['balance_check'] = True
        kwargs['context'] = ctx
        return super(AccountBankStatement, self).balance_check(
            *args, **kwargs)
