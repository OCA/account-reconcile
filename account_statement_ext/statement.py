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
import datetime
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields
from openerp.osv import fields, osv

class AccountStatementProfil(Model):
    """
    A Profile will contain all infos related to the type of
    bank statement, and related generated entries. It defines the
    journal to use, the partner and commision account and so on.
    """
    _name = "account.statement.profile"
    _description = "Statement Profil"
    
    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'partner_id': fields.many2one('res.partner',
                                      'Bank/Payment Office partner',
                                      help="Put a partner if you want to have it on the commission move \
                                      (and optionaly on the counterpart of the intermediate/banking move \
                                      if you tic the corresponding checkbox)."),
        'journal_id': fields.many2one('account.journal',
                                      'Financial journal to use for transaction',
                                      required=True),
        'commission_account_id': fields.many2one('account.account',
                                                         'Commission account',
                                                         required=True),
        'commission_analytic_id': fields.many2one('account.analytic.account',
                                                         'Commission analytic account'),
        'receivable_account_id': fields.many2one('account.account',
                                                        'Force Receivable/Payable Account',
                                                        help="Choose a receivable account to force the default\
                                                        debit/credit account (eg. an intermediat bank account instead of\
                                                        default debitors)."),
        'force_partner_on_bank': fields.boolean('Force partner on bank move', 
                                                    help="Tic that box if you want to use the credit insitute partner\
                                                    in the counterpart of the intermediat/banking move."
                                                    ),
        'balance_check': fields.boolean('Balance check', 
                                                    help="Tic that box if you want OpenERP to control the start/end \
                                                    balance before confirming a bank statement. If don't ticked, no \
                                                    balance control will be done."
                                                    ),
        'bank_statement_prefix': fields.char('Bank Statement Prefix', size=32),
        'bank_statement_ids': fields.one2many('account.bank.statement', 'profile_id', 'Bank Statement Imported'),
        
        
    }
    
    def _check_partner(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.partner_id == False and obj.force_partner_on_bank:
            return False
        return True

    _constraints = [
        (_check_partner, "You need to put a partner if you tic the 'Force partner on bank move' !", []),
    ]


class AccountBankSatement(Model):
    """
    We improve the bank statement class mostly for : 
    - Removing the period and compute it from the date of each line. 
    - Allow to remove the balance check depending on the chosen profile
    - Report errors on confirmation all at once instead of crashing onr by one
    - Add a profile notion that can change the generated entries on statement 
      confirmation.
     For this, we had to override quite some long method and we'll need to maintain
     them up to date. Changes are point up by '#Chg' comment.
     """

    _inherit = "account.bank.statement"
    
    _columns = {
        'profile_id': fields.many2one('account.statement.profile',
                                  'Profil', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'credit_partner_id': fields.related(
                        'profile_id', 
                        'partner_id', 
                        type='many2one', 
                        relation='res.partner', 
                        string='Financial Partner', 
                        store=True, readonly=True),
        'balance_check': fields.related(
                        'profile_id', 
                        'balance_check', 
                        type='boolean', 
                        string='Balance check', 
                        store=True, readonly=True),
        'journal_id':   fields.related(
                        'profile_id', 
                        'journal_id', 
                        type='many2one',
                        relation='account.journal', 
                        string='Journal', 
                        store=True, readonly=True),
        'period_id': fields.many2one('account.period', 'Period', required=False, readonly=True),
    }

    _defaults = {
        'period_id': lambda *a: False,
    }
    
    def create(self, cr, uid, vals, context=None):
        """Need to pass the journal_id in vals anytime because of account.cash.statement
        need it."""
        if 'profile_id' in vals:
            profile_obj = self.pool.get('account.statement.profile')
            profile = profile_obj.browse(cr,uid,vals['profile_id'],context)
            vals['journal_id'] = profile.journal_id.id
        return super(AccountBankSatement, self).create(cr, uid, vals, context=context)
    
    def _get_period(self, cursor, uid, date, context=None):
        """
        Find matching period for date, used in the statement line creation.
        """
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cursor, uid, dt=date, context=context)
        return periods and periods[0] or False
        
    def _check_company_id(self, cr, uid, ids, context=None):
        """
        Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if (statement.period_id and
                statement.company_id.id != statement.period_id.company_id.id):
                return False
            for line in statement.line_ids:
                if (line.period_id and
                    statement.company_id.id != line.period_id.company_id.id):
                    return False
        return True

    _constraints = [
        (_check_company_id, 'The journal and period chosen have to belong to the same company.', ['journal_id','period_id']),
    ]

    def button_cancel(self, cr, uid, ids, context={}):
        """
        We cancel the related move, delete them and finally put the
        statement in draft state. So no need to unreconcile all entries,
        then unpost them, then finaly cancel the bank statement.
        """
        done = []
        for st in self.browse(cr, uid, ids, context=context):
            if st.state=='draft':
                continue
            ids = []
            for line in st.line_ids:
                for move in line.move_ids:
                    if move.state <> 'draft':
                        move.button_cancel(context=context)
                    move.unlink(context=context)
            done.append(st.id)
        self.write(cr, uid, done, {'state':'draft'}, context=context)
        return True

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, context=None):
        """
        Override a large portion of the code to compute the periode for each line instead of
        taking the period of the whole statement.
        Remove the entry posting on generated account moves.
        We change the move line generated from the lines depending on the profile:
          - If receivable_account_id is set, we'll use it instead of the "partner" one
          - If partner_id is set, we'll us it for the commission (when imported throufh the wizard)
          - If partner_id is set and force_partner_on_bank is ticked, we'll let the partner of each line
            for the debit line, but we'll change it on the credit move line for the choosen partner_id
            => This will ease the reconciliation process with the bank as the partner will match the bank
            statement line
        
        :param int/long: st_line_id: account.bank.statement.line ID
        :param int/long: company_currency_id: res.currency ID
        :param char: st_line_number: that will be used as the name of the generated account move
        :return: int/long: ID of the created account.move
        """
        if context is None:
            context = {}
        res_currency_obj = self.pool.get('res.currency')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')     # Chg
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id, context=context) # Chg
        st = st_line.statement_id

        context.update({'date': st_line.date})
        ctx = context.copy()                        # Chg
        ctx['company_id'] = st_line.company_id.id   # Chg
        period_id = self._get_period(               # Chg
            cr, uid, st_line.date, context=ctx)  
            
        move_id = account_move_obj.create(cr, uid, {
            'journal_id': st.journal_id.id,
            'period_id': period_id,                 # Chg
            'date': st_line.date,
            'name': st_line_number,
            'ref': st_line.ref,
        }, context=context)
        account_bank_statement_line_obj.write(cr, uid, [st_line.id], {  # Chg
            'move_ids': [(4, move_id, False)]
        })

        torec = []
        if st_line.amount >= 0:
            account_id = st.journal_id.default_credit_account_id.id
        else:
            account_id = st.journal_id.default_debit_account_id.id

        acc_cur = ((st_line.amount<=0) and st.journal_id.default_debit_account_id) or st_line.account_id
        context.update({
                'res.currency.compute.account': acc_cur,
            })
        amount = res_currency_obj.compute(cr, uid, st.currency.id,
                company_currency_id, st_line.amount, context=context)

        val = {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': ((st_line.partner_id) and st_line.partner_id.id) or False,
            'account_id': (st_line.account_id) and st_line.account_id.id,
            'credit': ((amount>0) and amount) or 0.0,
            'debit': ((amount<0) and -amount) or 0.0,
            # Replace with the treasury one instead of bank  #Chg
            'statement_id': st.id,        
            'journal_id': st.journal_id.id,
            'period_id': period_id,                 #Chg
            'currency_id': st.currency.id,
            'analytic_account_id': st_line.analytic_account_id and st_line.analytic_account_id.id or False
        }

        if st.currency.id <> company_currency_id:
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                        st.currency.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        if st_line.account_id and st_line.account_id.currency_id and st_line.account_id.currency_id.id <> company_currency_id:
            val['currency_id'] = st_line.account_id.currency_id.id
            amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                    st_line.account_id.currency_id.id, amount, context=context)
            val['amount_currency'] = -amount_cur

        move_line_id = account_move_line_obj.create(cr, uid, val, context=context)
        torec.append(move_line_id)

        # Fill the secondary amount/currency
        # if currency is not the same than the company
        amount_currency = False
        currency_id = False
        if st.currency.id <> company_currency_id:
            amount_currency = st_line.amount
            currency_id = st.currency.id
        # GET THE RIGHT PARTNER ACCORDING TO THE CHOSEN PROFIL                              # Chg
        if st.profile_id.force_partner_on_bank:                                       # Chg
            bank_parrtner_id = st.profile_id.partner_id.id                            # Chg
        else:                                                                               # Chg
            bank_parrtner_id = ((st_line.partner_id) and st_line.partner_id.id) or False    # Chg
        
        account_move_line_obj.create(cr, uid, {
            'name': st_line.name,
            'date': st_line.date,
            'ref': st_line.ref,
            'move_id': move_id,
            'partner_id': bank_parrtner_id,                                                 # Chg
            'account_id': account_id,
            'credit': ((amount < 0) and -amount) or 0.0,
            'debit': ((amount > 0) and amount) or 0.0,
            # Replace with the treasury one instead of bank  #Chg
            'statement_id': st.id,       
            'journal_id': st.journal_id.id,
            'period_id': period_id,                 #Chg
            'amount_currency': amount_currency,
            'currency_id': currency_id,
            }, context=context)

        for line in account_move_line_obj.browse(cr, uid, [x.id for x in
                account_move_obj.browse(cr, uid, move_id,
                    context=context).line_id],
                context=context):
            if line.state <> 'valid':
                raise osv.except_osv(_('Error !'),
                        _('Journal item "%s" is not valid.') % line.name)

        # Bank statements will not consider boolean on journal entry_posted
        account_move_obj.post(cr, uid, [move_id], context=context)
        return move_id

    def _get_st_number_period_profile(self, cr, uid, date, profile_id):
        """
        Retrieve the name of bank statement from sequence, according to the period 
        corresponding to the date passed in args. Add a prefix if set in the profile.
        
        :param: date: date of the statement used to compute the right period
        :param: int/long: profile_id: the account.statement.profile ID from which to take the
                          bank_statement_prefix for the name
        :return: char: name of the bank statement (st_number)
        
        """
        year = self.pool.get('account.period').browse(cr, uid, self._get_period(cr, uid, date)).fiscalyear_id.id
        profile = self.pool.get('account.statement.profile').browse(cr,uid, profile_id)
        c = {'fiscalyear_id': year}
        obj_seq = self.pool.get('ir.sequence')
        journal_sequence_id = profile.journal_id.sequence_id and profile.journal_id.sequence_id.id or False
        if journal_sequence_id:
            st_number = obj_seq.next_by_id(cr, uid, journal_sequence_id, context=c)
        else:
            st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)
        if profile.bank_statement_prefix:
            st_number = profile.bank_statement_prefix + st_number
        return st_number

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """
        Completely override the method in order to have
        an error message which displays all the messages
        instead of having them pop one by one.
        We have to copy paste a big block of code, changing the error
        stack + managing period from date.
        
        TODO: Log the error in a bank statement field instead of using a popup !
        """
        # obj_seq = self.pool.get('irerrors_stack.sequence')
        if context is None:
            context = {}
        for st in self.browse(cr, uid, ids, context=context):

            j_type = st.journal_id.type
            company_currency_id = st.journal_id.company_id.currency_id.id
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue
            
            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))

            if not st.name == '/':
                st_number = st.name
            else:
# Begin Changes                
                st_number = self._get_st_number_period_profile(cr, uid, st.date, st.profile_id.id)
# End Changes 
            for line in st.move_line_ids:
                if line.state <> 'valid':
                    raise osv.except_osv(_('Error !'),
                            _('The account entries lines are not in valid state.'))
# begin changes
            errors_stack = []
            for st_line in st.line_ids:
                try:
                    if st_line.analytic_account_id:
                        if not st.journal_id.analytic_journal_id:
                            raise osv.except_osv(_('No Analytic Journal !'),
                                             _("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
                    if not st_line.amount:
                        continue
                    st_line_number = self.get_next_st_line_number(cr, uid, st_number, st_line, context)
                    self.create_move_from_st_line(cr, uid, st_line.id, company_currency_id, st_line_number, context)
                except osv.except_osv, exc:
                    msg = "Line ID %s with ref %s had following error: %s" % (st_line.id, st_line.ref, exc.value)
                    errors_stack.append(msg)
                except Exception, exc:
                    msg = "Line ID %s with ref %s had following error: %s" % (st_line.id, st_line.ref, str(exc))
                    errors_stack.append(msg)
            if errors_stack:
                msg = u"\n".join(errors_stack)
                raise osv.except_osv(_('Error'), msg)
#end changes
            self.write(cr, uid, [st.id], {
                    'name': st_number,
                    'balance_end_real': st.balance_end
            }, context=context)
            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal items are created.') % (st_number,))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def get_account_for_counterpart(self, cursor, uid,
            amount, account_receivable, account_payable):
        """
        Give the amount, payable and receivable account (that can be found using
        get_default_pay_receiv_accounts method) and receive the one to use. This method
        should be use when there is no other way to know which one to take.
        
        :param float: amount of the line
        :param int/long: account_receivable the  receivable account 
        :param int/long: account_payable the payable account 
        :return: int/long :the default account to be used by statement line as the counterpart
                 of the journal account depending on the amount.
        """
        account_id = False
        if amount >= 0:
            account_id = account_receivable
        else:
            account_id = account_payable
        if not account_id:
            raise osv.except_osv(
                _('Can not determine account'),
                _('Please ensure that minimal properties are set')
            )
        return account_id

    def get_default_pay_receiv_accounts(self, cursor, uid, context=None):
        """
        We try to determine default payable/receivable accounts to be used as counterpart
        from the company default propoerty. This is to be used if there is no otherway to 
        find the good one, or to find a default value that will be overriden by a completion 
        method (rules of account_statement_base_completion) afterwards.
        
        :return: tuple of int/long ID that give account_receivable, account_payable based on
                 company default.
        """
        account_receivable = False
        account_payable = False
        context = context or {}
        property_obj = self.pool.get('ir.property')
        model_fields_obj = self.pool.get('ir.model.fields')
        model_fields_ids = model_fields_obj.search(
            cursor,
            uid,
            [('name', 'in', ['property_account_receivable',
                             'property_account_payable']),
             ('model', '=', 'res.partner'),],
            context=context
        )
        property_ids = property_obj.search(
                    cursor,
                    uid, [
                            ('fields_id', 'in', model_fields_ids),
                            ('res_id', '=', False),
                        ],
                    context=context
        )
        
        for erp_property in property_obj.browse(cursor, uid,
            property_ids, context=context):
            if erp_property.fields_id.name == 'property_account_receivable':
                account_receivable = erp_property.value_reference.id
            elif erp_property.fields_id.name == 'property_account_payable':
                account_payable = erp_property.value_reference.id
        return account_receivable, account_payable

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        """
        Balance check depends on the profile. If no check for this profile is required,
        return True and do nothing, otherwise call super.
        
        :param int/long st_id: ID of the concerned account.bank.statement 
        :param char: journal_type that concern the bank statement
        :return: True
        """
        st = self.browse(cr, uid, st_id, context=context)
        if st.balance_check:
            return super(AccountBankSatement,self).balance_check(cr, uid, st_id, journal_type, context)
        else:
            return True

    def onchange_imp_config_id(self, cr, uid, ids, profile_id, context=None):
        """
        Compute values on the change of the profile.
        
        :param: int/long: profile_id that changed
        :return dict of dict with key = name of the field
        """
        if not profile_id:
            return {}
        import_config = self.pool.get("account.statement.profile").browse(cr,uid,profile_id)
        journal_id = import_config.journal_id.id
        account_id = import_config.journal_id.default_debit_account_id.id
        credit_partner_id = import_config.partner_id and import_config.partner_id.id or False
        return {'value': {'journal_id':journal_id, 'account_id': account_id,
                    'balance_check':import_config.balance_check,
                    'credit_partner_id':credit_partner_id,
                    }}


class AccountBankSatementLine(Model):
    """
    Override to compute the period from the date of the line, add a method to retrieve
    the values for a line from the profile. Override the on_change method to take care of 
    the profile when fullfilling the bank statement manually. Set the reference to 64 
    Char long instead 32.
    """
    _inherit = "account.bank.statement.line"

    def _get_period(self, cursor, user, context=None):
        """
        Return a period from a given date in the context.
        """
        date = context.get('date', None)
        periods = self.pool.get('account.period').find(cursor, user, dt=date)
        return periods and periods[0] or False

    def _get_default_account(self, cursor, user, context=None):
        return self.get_values_for_line(cursor, user, context = context)['account_id']
        
    _columns = {
        # Set them as required + 64 char instead of 32
        'ref': fields.char('Reference', size=64, required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True),
    }
    _defaults = {
        'period_id': _get_period,
        'account_id': _get_default_account,
    }
    
    def get_values_for_line(self, cr, uid, profile_id = False, partner_id = False, line_type = False, amount = False, context = None):
        """
        Return the account_id to be used in the line of a bank statement. It'll base the result as follow:
            - If a receivable_account_id is set in the profile, return this value and type = general
            - Elif line_type is given, take the partner receivable/payable property (payable if type= supplier, receivable
              otherwise)
            - Elif amount is given, take the partner receivable/payable property (receivable if amount >= 0.0,
              payable otherwise). In that case, we also fullfill the type (receivable = customer, payable = supplier)
              so it is easier for the accountant to know why the receivable/payable has been chosen
            - Then, if no partner are given we look and take the property from the company so we always give a value
              for account_id. Note that in that case, we return the receivable one.
        
        :param int/long profile_id of the related bank statement
        :param int/long partner_id of the line
        :param char line_type: a value from: 'general', 'supplier', 'customer'
        :param float: amount of the line
        :return: A dict of value that can be passed directly to the write method of
                 the statement line:
                     {'partner_id': value,
                      'account_id' : value,
                      'type' : value,
                       ...
                     }
        """
        if context is None:
            context = {}
        res = {}
        obj_partner = self.pool.get('res.partner')
        obj_stat = self.pool.get('account.bank.statement')
        receiv_account = pay_account = account_id = False
        # If profile has a receivable_account_id, we return it in any case
        if profile_id:
            profile = self.pool.get("account.statement.profile").browse(cr,uid,profile_id)
            if profile.receivable_account_id:
                res['account_id'] = profile.receivable_account_id.id 
                res['type'] = 'general'
                return res
        # If partner -> take from him
        if partner_id:
            part = obj_partner.browse(cr, uid, partner_id, context=context)
            pay_account = part.property_account_payable.id
            receiv_account = part.property_account_receivable.id
        # If no value, look on the default company property
        if not pay_account or not receiv_account:
            receiv_account, pay_account = obj_stat.get_default_pay_receiv_accounts(cr, uid, context=None)
        # Now we have both pay and receive account, choose the one to use
        # based on line_type first, then amount, otherwise take receivable one.
        if line_type is not False:
            if line_type == 'supplier':
                res['account_id'] = pay_account
            else:
                res['account_id'] = receiv_account
        elif amount is not False:
            if amount >= 0:
                res['account_id'] = receiv_account
                res['type'] = 'customer'
            else:
                res['account_id'] = pay_account
                res['type'] = 'supplier'
        if not account_id:
           res['account_id'] = receiv_account
        return res
        
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, profile_id, context=None):
        """
        Override of the basic method as we need to pass the profile_id in the on_change_type
        call.
        """
        obj_partner = self.pool.get('res.partner')
        if context is None:
            context = {}
        if not partner_id:
            return {}
        part = obj_partner.browse(cr, uid, partner_id, context=context)
        if not part.supplier and not part.customer:
            type = 'general'
        elif part.supplier and part.customer:
            type = 'general'
        else:
            if part.supplier == True:
                type = 'supplier'
            if part.customer == True:
                type = 'customer'
        res_type = self.onchange_type(cr, uid, ids, partner_id, type, profile_id, context=context) # Chg
        if res_type['value'] and res_type['value'].get('account_id', False):
            return {'value': {'type': type, 'account_id': res_type['value']['account_id']}}
        return {'value': {'type': type}}
        
    def onchange_type(self, cr, uid, line_id, partner_id, type, profile_id, context=None):
        """
        Keep the same features as in standard and call super. If an account is returned,
        call the method to compute line values.
        """
        if context is None:
            context = {}
        res = super(AccountBankSatementLine,self).onchange_type(cr, uid, line_id, partner_id, type, context)
        if 'account_id' in res['value']:
            result = self.get_values_for_line(cr, uid, profile_id = profile_id, 
                partner_id = partner_id, line_type = type, context = context)
            if result:
                res['value'].update({'account_id':result['account_id']})
        return res

