# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Joel Grand-Guillaume
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

"""
Wizard to import financial institute date in bank statement
"""

from osv import fields, osv
from tools.translate import _
import os

class CreditPartnerStatementImporter(osv.osv_memory):
    """Import Credit statement"""

    _name = "credit.statement.import"
    
    def _get_profile(self, cr, uid, context=None):
        if context is None: context = {}
        res = False
        if (context.get('active_model', False) == 'account.statement.profil' and
            context.get('active_ids', False)):
            res = context['active_ids']
            if len(res) > 1:
                raise Exception (_('You cannot use this on more than one profile !'))
        return res[0]
    
    _columns = {
        
        'profile_id': fields.many2one('account.statement.profil',
                                      'Import configuration parameter',
                                      required=True),
        'input_statement': fields.binary('Statement file', required=True),
        'partner_id': fields.many2one('res.partner',
                                      'Credit insitute partner',
                                      ),
        'journal_id': fields.many2one('account.journal',
                                      'Financial journal to use transaction',
                                      ),
        'input_statement': fields.binary('Statement file', required=True),
        'file_name': fields.char('File Name', size=128),
        'commission_account_id': fields.many2one('account.account',
                                                         'Commission account',
                                                         ),
        'commission_analytic_id': fields.many2one('account.analytic.account',
                                                     'Commission analytic account',
                                                 ),
        'receivable_account_id': fields.many2one('account.account',
                                                 'Force Receivable/Payable Account'),
        'force_partner_on_bank': fields.boolean('Force partner on bank move', 
                                                    help="Tic that box if you want to use the credit insitute partner\
                                                    in the counterpart of the treasury/banking move."
                                                    ),
        'balance_check': fields.boolean('Balance check', 
                                                    help="Tic that box if you want OpenERP to control the start/end balance\
                                                    before confirming a bank statement. If don't ticked, no balance control will be done."
                                                    ),

    }   
    
    _defaults = {
        'profile_id': _get_profile,
    }

    def onchange_profile_id(self, cr, uid, ids, profile_id, context=None):
        res={}
        if profile_id:
            c = self.pool.get("account.statement.profil").browse(cr,uid,profile_id)
            res = {'value': {'partner_id': c.partner_id and c.partner_id.id or False,
                    'journal_id': c.journal_id and c.journal_id.id or False, 'commission_account_id': \
                    c.commission_account_id and c.commission_account_id.id or False, 
                    'receivable_account_id': c.receivable_account_id and c.receivable_account_id.id or False,
                    'commission_a':c.commission_analytic_id and c.commission_analytic_id.id or False,
                    'force_partner_on_bank':c.force_partner_on_bank,
                    'balance_check':c.balance_check,}}
        return res

    def _check_extension(self, filename):
        (shortname, ftype) = os.path.splitext(file_name)
        if not ftype:
            #We do not use osv exception we do not want to have it logged
            raise Exception(_('Please use a file with an extention'))
        return ftype

    def import_statement(self, cursor, uid, req_id, context=None):
        """This Function import credit card agency statement"""
        context = context or {}
        if isinstance(req_id, list):
            req_id = req_id[0]
        importer = self.browse(cursor, uid, req_id, context)
        ftype = self._check_extension(importer.file_name)
        sid = self.pool.get(
                'account.bank.statement').statement_import(
                                            cursor,
                                            uid,
                                            False,
                                            importer.profile_id.id,
                                            importer.input_statement,
                                            ftype.replace('.',''),
                                            context=context
        )
        # obj_data = self.pool.get('ir.model.data')
        #         act_obj = self.pool.get('ir.actions.act_window')
        #         result = obj_data.get_object_reference(cursor, uid, 'account_statement_import', 'action_treasury_statement_tree')
        #         
        #         id = result and result[1] or False
        #         result = act_obj.read(cursor, uid, [id], context=context)[0]
        #         result['domain'] = str([('id','in',[sid])])
        
        # We should return here the profile for which we executed the import
        return {'type': 'ir.actions.act_window_close'}
