# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Joel Grand-Guillaume                                              #
#   Copyright 2011-2012 Camptocamp SA                                         #
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv import orm
from tools.translate import _
from openerp.addons.account_statement_base_completion.statement import \
    ErrorTooManyPartner


class AccountStatementCompletionRule(orm.Model):

    _name = "account.statement.completion.rule"
    _inherit = "account.statement.completion.rule"

    def _get_functions(self, cr, uid, context=None):
        res = super(AccountStatementCompletionRule, self)._get_functions(
            cr, uid, context=context)
        res.append(
            ('get_from_ref_and_so', 'From line reference (based on SO number)')
        )
        return res

    # Should be private but data are initialised with no update XML
    def get_from_ref_and_so(self, cr, uid, st_line, context=None):
        """
        Match the partner based on the SO number and the reference of the
        statement line. Then, call the generic get_values_for_line method to
        complete other values. If more than one partner matched, raise the
        ErrorTooManyPartner error.

        :param int/long st_line: read of the concerned
        account.bank.statement.line

        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        st_obj = self.pool['account.bank.statement.line']
        res = {}
        if st_line:
            so_obj = self.pool.get('sale.order')
            so_id = so_obj.search(
                cr, uid, [('name', '=', st_line['ref'])], context=context)
            if so_id:
                if so_id and len(so_id) == 1:
                    so = so_obj.browse(cr, uid, so_id[0], context=context)
                    res['partner_id'] = so.partner_id.id
                elif so_id and len(so_id) > 1:
                    raise ErrorTooManyPartner(
                        _('Line named "%s" (Ref:%s) was matched by more '
                          'than one partner while looking on SO by ref.') %
                        (st_line['name'], st_line['ref']))
                st_vals = st_obj.get_values_for_line(
                    cr, uid, profile_id=st_line['profile_id'],
                    master_account_id=st_line['master_account_id'],
                    partner_id=res.get('partner_id', False),
                    line_type='customer',
                    amount=st_line['amount'] if st_line['amount'] else 0.0,
                    context=context)
                res.update(st_vals)
        return res
