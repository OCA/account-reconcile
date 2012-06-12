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
from tools.translate import _
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields

class AccountStatementProfil(Model):
    _inherit = "account.statement.profil"
    
    _columns={
        # For now, we don't implement this features, but this would probably be there:
        # 'auto_completion': fields.text('Auto Completion'),
        # 'transferts_account_id':fields.many2one('account.account', 'Transferts Account'),
        
        'rule_ids':fields.many2many('account.statement.completion.rule', 
            rel='account_statement_rule_statement_profile_to_rel', 
            'profile_id','rule_id',
            'Related statement profiles'),
    }
    
    def find_partner_by_rules(self, cr, uid, ids, field_value, context=None):
        """This method will execute all rules, in their sequence order, 
        to match a partner for the given statement.line and return his id."""
        if not context:
            context={}
        partner_id = False
        for profile in self.browse(cr, uid, ids, context=context):
            for rule in profile.rule_ids:
                method_to_call = getattr(rule, rule.function_to_call)
                partner_id = method_to_call(cr,uid,field_value,context)
                if partner_id:
                    return partner_id
        return partner_id
        

class AccountStatementCompletionRule(Model):
    """This will represent all the completion method that we can have to
    fullfill the bank statement. You'll be able to extend them in you own module
    and choose those to apply for every statement profile."""
    
    _name = "account.statement.completion.rule"
    _order = "sequence asc"
    
    _get_functions = [('get_from_label_and_partner_field', 'From line label (based on partner field)'),\
        ('in', 'External -> OpenERP'), ('out', 'External <- OpenERP')]
    
    _columns={
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name')
        'profile_ids':fields.many2many('account.statement.profil', 
            rel='account_statement_rule_statement_profile_to_rel', 
            'rule_id', 'profile_id',
            'Related statement profiles'),
        'function_to_call': fields.selection(_get_functions, 'Type'),
    }
    
    def get_from_label_and_partner_field(self, cr, uid, field_value, context=None):
        """Match the partner based on the label field of the statement line
        and the text defined in the 'bank_statement_label' field of the partner.
        Remember that we can have values separated with ;"""
        partner_obj = self.pool.get('res.partner')
        ids = partner_obj.search(cr, uid, [['bank_statement_label', '!=', False]], context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            for partner_label in partner.bank_statement_label.split(';'):
                if partner_label in field_value:
                    return partner.id
        return False

    def get_from_label_and_partner_name(self, cr, uid, field_value, context=None):
        """Match the partner based on the label field of the statement line
        and the name of the partner."""
        supplier_ids = self.search(cr, uid, [['supplier', '=', True]], context=context)
        sql = """SELECT id FROM res_partner WHERE name ilike """
        for partner in self.browse(cr, uid, supplier_ids, context=context):
            if partner.name in label:
                return partner.id
        return False
       
    
class AccountStatementLine(Model):
    """Add sparse field on the statement line to allow to store all the
    bank infos that are given by an office. You can then add you own in your
    module."""
    _inherit = "account.bank.statement.line"

    _columns={
        # 'email_address': fields.char('Email', size=64),
        #         'order_ref': fields.char('Order Ref', size=64),
        #         'partner_name': fields.char('Partner Name', size=64),
        # 
        # Only label for a start, but other module can add their own
        'additionnal_bank_fields' : fields.serialized('Additionnal infos from bank', help="Used by completion and import system."),
        'label': fields.sparse(type='char', string='Label', 
            serialization_field='additionnal_bank_fields'),
        
    }
    
    
    
    def auto_complete_line(self, cr, uid, line, context=None):
        res={}
        if not line.partner_id or line.account_id.id ==1:
            partner_obj = self.pool.get('res.partner')
            partner_id=False
            if line.order_ref:
                partner_id = partner_obj.get_partner_from_order_ref(cr, uid, line.order_ref, context=context)
            if not partner_id and line.email_address:
                partner_id = partner_obj.get_partner_from_email(cr, uid, line.email_address, context=context)
            if not partner_id and line.partner_name:
                partner_id = partner_obj.get_partner_from_name(cr, uid, line.partner_name, context=context)
            if not partner_id and line.label:
                partner_id = partner_obj.get_partner_from_label_based_on_bank_statement_label(cr, uid, line.label, context=context)
            if partner_id:
                res = {'partner_id': partner_id}
            if context['auto_completion']:
                #Build the space for expr
                space = {
                            'self':self,
                            'cr':cr,
                            'uid':uid,
                            'line': line,
                            'res': res,
                            'context':context,
                        }
                exec context['auto_completion'] in space
                if space.get('result', False):
                    res.update(space['result'])
        return res
    
class A(object):
    def xx_toto():
        print 'toto'
        

a = A()
funcs = ['yy_toto', 'xx_toto']
for i in funcs:
    if hasattr(a, i):
        to_call = getattr(a, i)
        to_call()
    else:
        raise NameError('blblblb')

class AccountBankSatement(Model):
   """We add a basic button and stuff to support the auto-completion
   of the bank statement once line have been imported or manually entred.
   """
    _inherit = "account.bank.statement"


    def button_auto_completion(self, cr, uid, ids, context=None):
        if not context:
            context={}
        stat_line_obj = self.pool.get('account.bank.statement.line')
        for stat in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            if stat.bank_statement_import_id:
                ctx['partner_id'] = stat.bank_statement_import_id.partner_id.id
                ctx['transferts_account_id'] = stat.bank_statement_import_id.transferts_account_id.id
                ctx['credit_account_id'] = stat.bank_statement_import_id.credit_account_id.id
                ctx['fee_account_id'] = stat.bank_statement_import_id.fee_account_id.id
                ctx['auto_completion'] = stat.bank_statement_import_id.auto_completion
            for line in stat.line_ids:
                vals = stat_line_obj.auto_complete_line(cr, uid, line, context=ctx)
                if not line.ref and not vals.get('ref', False):
                    vals['ref'] = stat.name
                if vals:
                    stat_line_obj.write(cr, uid, line.id, vals, context=ctx)
        return True

    def auto_confirm(self, cr, uid, ids, context=None):
        if not context:
            context={}
        ok=True
        for stat in self.browse(cr, uid, ids, context=context):
            for line in stat.line_ids:
                if not line.partner_id or line.account_id.id == 1:
                    ok=False
                    continue
            if ok:
                self.button_confirm(cr, uid, [stat.id], context=context)
        return True
