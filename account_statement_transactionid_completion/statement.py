# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
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

from tools.translate import _
import datetime
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields
from openerp.addons.account_statement_base_completion.statement import ErrorTooManyPartner

class AccountStatementCompletionRule(Model):
    """Add a rule based on transaction ID"""
    
    _inherit = "account.statement.completion.rule"
    
    def _get_functions(self):
        res = super (self,AccountStatementCompletionRule)._get_functions()
        res.append(('get_from_transaction_id_and_so', 'From line reference (based on SO transaction ID'))
        return res

    _columns={
        'function_to_call': fields.selection(_get_functions, 'Method'),
    }
    
    #TODO : Ensure we match only one partner => Otherwise raise an error !!!
    def get_from_transaction_id_and_so(self, cr, uid, line_id, context=None):
        """Match the partner based on the transaction ID field of the SO.
        Then, call the generic st_line method to complete other values.
        In that case, we always fullfill the reference of the line with the SO name.
        Return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
            """
        st_obj = self.pool.get('account.bank.statement.line')
        st_line = st_obj.browse(cr,uid,line_id)
        res = {}
        if st_line:
            so_obj = self.pool.get('sale.order')
            so_id = so_obj.search(cursor, uid, [('transaction_id', '=', st_line.transaction_id)])
            if so_id and len(so_id) == 1:
                so = so_obj.browse(cursor, uid, so_id[0])
                res['partner_id'] = so.partner_id.id
                res['ref'] = so.name
            elif so_id and len(so_id) > 1:
                raise Exception(_('Line named "%s" was matched by more than one partner.')%(st_line.name,st_line.id))
            if so_id:
                st_vals = st_obj.get_values_for_line(cr, uid, profile_id = st_line.statement_id.profile_id.id,
                    partner_id = res.get('partner_id',False), line_type = st_line.type, st_line.amount, context)
                res.update(st_vals)
        return res

 
class AccountStatementLine(Model):
    _inherit = "account.bank.statement.line"

    _columns={
        # 'additionnal_bank_fields' : fields.serialized('Additionnal infos from bank', help="Used by completion and import system."),
        'transaction_id': fields.sparse(type='char', string='Transaction ID', 
            size=128,
            serialization_field='additionnal_bank_fields',
            help="Transction id from the financial institute"),
    }





