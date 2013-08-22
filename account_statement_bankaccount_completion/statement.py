# -*- coding: utf-8 -*-
#
#
#    Author: Laurent Mignon
#    Copyright 2013 'ACSONE SA/NV'
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
#


from openerp.tools.translate import _
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.addons.account_statement_base_completion.statement import ErrorTooManyPartner


class AccountStatementCompletionRule(Model):

    """Add a rule based on transaction ID"""

    _inherit = "account.statement.completion.rule"

    def _get_functions(self, cr, uid, context=None):
        res = super(AccountStatementCompletionRule, self)._get_functions(
            cr, uid, context=context)
        res.append(('get_from_bank_account',
                    'From bank account number (Nomal or IBAN)'))
        return res

    _columns = {
        'function_to_call': fields.selection(_get_functions, 'Method'),
    }

    def get_from_bank_account(self, cr, uid, st_line, context=None):
        """
        Match the partner based on the partner account number field
        Then, call the generic st_line method to complete other values.
        In that case, we always fullfill the reference of the line with the SO name.
        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
            """
        if st_line['partner_acc_number'] == False:
            return {}
        st_obj = self.pool.get('account.bank.statement.line')
        res = {}
        res_bank = self.pool.get('res.partner.bank')
        ids = res_bank.search(cr,
                              uid,
                              [('acc_number', '=', st_line['partner_acc_number'])],
                              context=context)
        if len(ids) > 1:
            raise ErrorTooManyPartner(_('Line named "%s" (Ref:%s) was matched by more than '
                                        'one partner.') % (st_line['name'], st_line['ref']))
        if len(ids) == 1:
            partner = self.pool.get('res.partner.bank').browse(cr, uid, ids[0], context=context).partner_id
            res['partner_id'] = partner.id
            st_vals = st_obj.get_values_for_line(cr,
                                                 uid,
                                                 profile_id=st_line['profile_id'],
                                                 master_account_id=st_line['master_account_id'],
                                                 partner_id=res.get('partner_id', False),
                                                 line_type=st_line['type'],
                                                 amount=st_line['amount'] if st_line['amount'] else 0.0,
                                                 context=context)
            res.update(st_vals)
        return res


class AccountStatementLine(Model):
    _inherit = "account.bank.statement.line"

    _columns = {
        # 'additionnal_bank_fields' : fields.serialized('Additionnal infos from bank', help="Used by completion and import system."),
        'partner_acc_number': fields.sparse(
            type='char',
            string='Account Number',
            size=64,
            serialization_field='additionnal_bank_fields',
            help="Account number of the partner"),
        'partner_bank_bic': fields.sparse(
            type='char',
            string='Bank Identifier Code',
            size=16,
            serialization_field='additionnal_bank_fields',
            help="Bank Identifier Code"),
    }
