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


class ErrorTooManyPartner(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class AccountStatementProfil(Model):
    _inherit = "account.statement.profil"
    
    _columns={
        # For now, we don't implement this features, but this would probably be there:
        # 'auto_completion': fields.text('Auto Completion'),
        # 'transferts_account_id':fields.many2one('account.account', 'Transferts Account'),
        
        'rule_ids':fields.many2many('account.statement.completion.rule', 
            string='Related statement profiles',
            rel='account_statement_rule_statement_profile_to_rel', 
            ids1='profile_id',ids2='rule_id',
            ),
    }
    
    def find_values_from_rules(self, cr, uid, ids, line_id, context=None):
        """This method will execute all rules, in their sequence order, 
        to match a partner for the given statement.line and return his id.
        
        :param int/long line_id: eee
        :return: A dict of value that can be passed directly to the write method of
                 the statement line:
                     {'partner_id': value,
                      'account_id' : value,
                       ...
                     }
        """
        if not context:
            context={}
        res = {}
        for profile in self.browse(cr, uid, ids, context=context):
            for rule in profile.rule_ids:
                method_to_call = getattr(rule, rule.function_to_call)
                result = method_to_call(cr,uid,line_id,context)
                if result:
                    return res
        return res
        

class AccountStatementCompletionRule(Model):
    """This will represent all the completion method that we can have to
    fullfill the bank statement. You'll be able to extend them in you own module
    and choose those to apply for every statement profile.
    The goal of a rules is to fullfill at least the partner of the line, but
    if possible also the reference because we'll use it in the reconciliation 
    process. The reference should contain the invoice number or the SO number
    """
    
    _name = "account.statement.completion.rule"
    _order = "sequence asc"
    
    def _get_functions(self):
        """List of available methods for rules. Override this to add you own."""
        return [
            ('get_from_label_and_partner_field', 'From line label (based on partner field)'),
            ('get_from_label_and_partner_name', 'From line label (based on partner name)'),
            ]
    
    _columns={
        'sequence': fields.integer('Sequence', help="Lower means paresed first."),
        'name': fields.char('Name'),
        'profile_ids': fields.many2many('account.statement.profil', 
            rel='account_statement_rule_statement_profile_to_rel', 
            ids1='rule_id', ids2='profile_id',
            string='Related statement profiles'),
        'function_to_call': fields.selection(_get_functions, 'Method'),
    }

    def get_from_label_and_partner_field(self, cr, uid, line_id, context=None):
        """Match the partner based on the label field of the statement line
        and the text defined in the 'bank_statement_label' field of the partner.
        Remember that we can have values separated with ; Then, call the generic 
        st_line method to complete other values.
        If more than one partner matched, raise an error.
        Return:
            A dict of value that can be passed directly to the write method of
            the statement line.
           {'partner_id': value,
            'account_id' : value,
            ...}
            """
        partner_obj = self.pool.get('res.partner')
        st_obj = self.pool.get('account.bank.statement.line')
        st_line = st_obj.browse(cr,uid,line_id)
        res = {}
        compt = 0
        if st_line:
            ids = partner_obj.search(cr, uid, [['bank_statement_label', '!=', False]], context=context)
            for partner in self.browse(cr, uid, ids, context=context):
                for partner_label in partner.bank_statement_label.split(';'):
                    if partner_label in st_line.label:
                        compt += 1
                        res['partner_id'] = partner.id
                        if compt > 1:
                            raise ErrorTooManyPartner(_('Line named "%s" was matched by more than one partner.')%(st_line.name,st_line.id))
            st_vals = st_obj.get_values_for_line(cr, uid, profile_id = st_line.statement_id.profile_id.id,
                partner_id = res.get('partner_id',False), line_type = st_line.type, amount = st_line.amount, context = context)
            res.update(st_vals)
        return res

    def get_from_label_and_partner_name(self, cr, uid, line_id, context=None):
        """Match the partner based on the label field of the statement line
        and the name of the partner.
        Then, call the generic st_line method to complete other values.
        Return:
            A dict of value that can be passed directly to the write method of
            the statement line.
           {'partner_id': value,
            'account_id' : value,
            
            ...}
            """
        res = {}
        st_obj = self.pool.get('account.bank.statement.line')
        st_line = st_obj.browse(cr,uid,line_id)
        if st_line:
            sql = "SELECT id FROM res_partner WHERE name ~* '.*%s.*'"
            cr.execute(sql, (st_line.label,))
            result = cr.fetchall()
            if len(result) > 1:
                raise ErrorTooManyPartner(_('Line named "%s" was matched by more than one partner.')%(st_line.name,st_line.id))
            for id in result:
                res['partner_id'] = id
            st_vals = st_obj.get_values_for_line(cr, uid, profile_id = st_line.statement_id.profile_id.id,
                partner_id = res.get('partner_id',False), line_type = st_line.type, st_line.amount, context)
            res.update(st_vals)
        return res
       
    
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
    
    def get_line_values_from_rules(self, cr, uid, ids, context=None):
        """
        We'll try to find out the values related to the line based on what we
        have and rules setted on the profile..
        """
        profile_obj = self.pool.get('account.statement.profil')
        res={}
        errors_stack = []
        for line in self.browse(cr,uid, ids, context):
            try:
                vals = profile_obj.find_values_from_rules(cr, uid, ids, line.id, context)
                res[line.id]=vals
            except ErrorTooManyPartner, exc:
                msg = "Line ID %s had following error: %s" % (line.id, str(exc))
                errors_stack.append(msg)
            # if not auto_complete_line
            # if not line.partner_id or line.account_id.id ==1:
                # partner_obj = self.pool.get('res.partner')
                #                partner_id=False
                #                if line.order_ref:
                #                    partner_id = partner_obj.get_partner_from_order_ref(cr, uid, line.order_ref, context=context)
                #                if not partner_id and line.email_address:
                #                    partner_id = partner_obj.get_partner_from_email(cr, uid, line.email_address, context=context)
                #                if not partner_id and line.partner_name:
                #                    partner_id = partner_obj.get_partner_from_name(cr, uid, line.partner_name, context=context)
                #                if not partner_id and line.label:
                #                    partner_id = partner_obj.get_partner_from_label_based_on_bank_statement_label(cr, uid, line.label, context=context)
                #                if partner_id:
                #                    res = {'partner_id': partner_id}
                #                if context['auto_completion']:
                #                    #Build the space for expr
                #                    space = {
                #                                'self':self,
                #                                'cr':cr,
                #                                'uid':uid,
                #                                'line': line,
                #                                'res': res,
                #                                'context':context,
                #                            }
                #                    exec context['auto_completion'] in space
                #                    if space.get('result', False):
                #                        res.update(space['result'])
        if errors_stack:
            msg = u"\n".join(errors_stack)
            raise ErrorTooManyPartner(msg)
        return res
        
#         
# class A(object):
#     def xx_toto():
#         print 'toto'
#         
# 
# a = A()
# funcs = ['yy_toto', 'xx_toto']
# for i in funcs:
#     if hasattr(a, i):
#         to_call = getattr(a, i)
#         to_call()
#     else:
#         raise NameError('blblblb')

class AccountBankSatement(Model):
    """
    We add a basic button and stuff to support the auto-completion
    of the bank statement once line have been imported or manually entred.
    """
    _inherit = "account.bank.statement"

    def button_auto_completion(self, cr, uid, ids, context=None):
        if not context:
            context={}
        stat_line_obj = self.pool.get('account.bank.statement.line')
        errors_msg=False
        for stat in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            line_ids = map(lambda x:x.id, stat.line_ids)
            try:
                res = stat_line_obj.get_line_values_from_rules(cr, uid, line_ids, context=ctx)
            except ErrorTooManyPartner, exc:
                errors_msg = str(exc)
            for id in line_ids:
                vals = res[line.id]
                if vals:
                    stat_line_obj.write(cr, uid, id, vals, context=ctx)
            # cr.commit()
            # TOTEST: I don't know if this is working...
            if errors_msg:
                # raise osv.except_osv(_('Error'), errors_msg)
                warning = {
                    'title': _('Error!'),
                    'message' : errors_msg,
                }
                return {'warning': warning}
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
