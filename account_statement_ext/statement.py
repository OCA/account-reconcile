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
from account_statement_ext.file_parser.parser import FileParser
import datetime
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields

class AccountStatementProfil(Model):
    _name = "account.statement.profil"
    _description = "Statement Profil"
    
    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'partner_id': fields.many2one('res.partner',
                                      'Credit insitute partner',
                                      help="Put a partner if you want to have it on the commission move (and optionaly\
                                      on the counterpart of the intermediate/banking move if you tic the corresponding checkbox)."),
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
                                                    help="Tic that box if you want OpenERP to control the start/end balance\
                                                    before confirming a bank statement. If don't ticked, no balance control will be done."
                                                    ),
    }

    _defaults = {}

    def _check_partner(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.partner_id == False and obj.force_partner_on_bank:
            return False
        return True

    _constraints = [
        (_check_partner, "You need to put a partner if you tic the 'Force partner on bank move' !", []),
    ]


class AccountBankSatement(Model):
    """A kind of bank statement for intermediate move between customer and real bank, used
    for manageing check, payment office like paypal or marketplace like amazon.
    We inherit account.bank.statement because it's a very close object with only some 
    difference. But we want some method to be completely different, so we create a new object."""

    _inherit = "account.bank.statement"
    
    _columns = {
        'import_config_id': fields.many2one('account.statement.profil',
                                  'Profil', required=True, states={'draft': [('readonly', False)]}),
        'credit_partner_id': fields.related(
                        'import_config_id', 
                        'partner_id', 
                        type='many2one', 
                        relation='res.partner', 
                        string='Financial Partner', 
                        store=True, readonly=True),
        'balance_check': fields.related(
                        'import_config_id', 
                        'balance_check', 
                        type='boolean', 
                        string='Balance check', 
                        store=True, readonly=True),
        'journal_id':   fields.related(
                        'import_config_id', 
                        'journal_id', 
                        type='many2one',
                        relation='account.journal', 
                        string='Journal', 
                        store=True, readonly=True),
         # 'line_ids': fields.one2many('account.bank.statement.line',
         #                            'statement_id', 'Statement lines',
         #                            states={'confirm':[('readonly', True)]}),
        # 'move_line_ids': fields.one2many('account.move.line', 'statement_treasury_id',
        #             'Entry lines', states={'confirm':[('readonly',True)]}),
        # Redefine this field to avoid his computation (it is a function field on bank statement)
        # 'balance_end': fields.dummy(string="Computed Balance"),
        'period_id': fields.many2one('account.period', 'Period', required=False, readonly=True),
    }

    _defaults = {
        'period_id': lambda *a: False,
    }
    
    def create(self, cr, uid, vals, context=None):
        """Need to pass the journal_id in vals anytime because of account.cash.statement
        that need it."""
        if 'import_config_id' in vals:
            profil_obj = self.pool.get('account.statement.profil')
            profile = profil_obj.browse(cr,uid,vals['import_config_id'],context)
            vals['journal_id'] = profile.journal_id.id
        return super(AccountBankSatement, self).create(cr, uid, vals, context=context)
    
    def _get_period(self, cursor, uid, date, context=None):
        '''
        Find matching period for date, used in thestatement line creation.
        '''
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

    # Redefine the constraint, or it still refer to the original method
    _constraints = [
        (_check_company_id, 'The journal and period chosen have to belong to the same company.', ['journal_id','period_id']),
    ]

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, context=None):
        """Override a large portion of the code to compute the periode for each line instead of
        taking the period of the whole statement.
        Remove the entry posting on generated account moves.
        Point to account.bank.statement.line instead of account.bank.statement.line.
        In Treasury Statement, unlike the Bank statement, we will change the move line generated from the 
        lines depending on the profil (config import):
          - If receivable_account_id is set, we'll use it instead of the "partner" one
          - If partner_id is set, we'll us it for the commission (when imported throufh the wizard)
          - If partner_id is set and force_partner_on_bank is ticked, we'll let the partner of each line
            for the debit line, but we'll change it on the credit move line for the choosen partner_id
            => This will ease the reconsiliation process with the bank as the partner will match the bank
            statement line
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
        if st.import_config_id.force_partner_on_bank:                                       # Chg
            bank_parrtner_id = st.import_config_id.partner_id.id                            # Chg
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

    def _get_st_number_period(self, cr, uid, date, journal_sequence_id):
        """Retrieve the name of bank statement from sequence, according to the period 
        corresponding to the date passed in args"""
        year = self.pool.get('account.period').browse(cr, uid, self._get_period(cr, uid, date)).fiscalyear_id.id
        c = {'fiscalyear_id': year}
        obj_seq = self.pool.get('ir.sequence')
        if journal_sequence_id:
            st_number = obj_seq.next_by_id(cr, uid, journal_sequence_id, context=c)
        else:
            st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)
        return st_number

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """Completely override the method in order to have
           an error message which displays all the messages
           instead of having them pop one by one.
           We have to copy paste a big block of code, changing the error
           stack + managing period from date."""
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
                seq_id = st.journal_id.sequence_id and st.journal_id.sequence_id.id or False
                st_number = self._get_st_number_period(cr, uid, st.date, seq_id)
                # c = {'fiscalyear_id': st.period_id.fiscalyear_id.id}
                # if st.journal_id.sequence_id:
                #     st_number = obj_seq.next_by_id(cr, uid, st.journal_id.sequence_id.id, context=c)
                # else:
                #     st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)
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

    def get_partner_from_so(self, cursor, uid,transaction_id):
        """Look for the SO that has the given transaction_id, if not
        found, try to match the SO name instead. If still nothing, 
        return False"""
        so_obj = self.pool.get('sale.order')
        so_id = so_obj.search(cursor, uid, [('transaction_id', '=', transaction_id)])
        if so_id and len(so_id) == 1:
            return so_obj.browse(cursor, uid, so_id[0]).partner_id.id
        else:
            so_id2 = so_obj.search(cursor, uid, [('name', '=', transaction_id)])
            if so_id2 and len(so_id2) == 1:
                return so_obj.browse(cursor, uid, so_id2[0]).partner_id.id
        return False


    def get_default_accounts(self, cursor, uid, receivable_account_id, context=None):
        """We try to determine default accounts if not receivable_account_id set, otherwise
        take it for both receivable and payable account"""
        account_receivable = False
        account_payable = False
        if receivable_account_id:
            account_receivable = account_payable = receivable_account_id
        else:
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

    def _get_account_id(self, cursor, uid,
            amount, account_receivable, account_payable):
        "return the default account to be used by statement line"
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

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        """Balance check depends on the profil. If no check for this profil is required,
        return True"""
        st = self.browse(cr, uid, st_id, context=context)
        if st.balance_check:
            return super(AccountBankSatement,self).balance_check(cr, uid, st_id, journal_type, context)
        else:
            return True
        
    def _get_value_from_import_config(self, cr, uid, import_config_id):
        """Return a dict with with values taken from the given config. 
        e.g. (journal_id, partner_id, commission_account_id, mode, forced_account_id)
        """
        # Get variable from config
        import_config = self.pool.get("account.statement.profil").browse(cr,uid,import_config_id)
        forced_account_id = import_config.receivable_account_id and import_config.receivable_account_id.id or False
        journal_id = import_config.journal_id and import_config.journal_id.id or False
        partner_id = import_config.partner_id and import_config.partner_id.id or False
        commission_account_id = import_config.commission_account_id.id
        commission_analytic_id = import_config.commission_analytic_id and import_config.commission_analytic_id.id or False
        force_partner_on_bank = import_config.force_partner_on_bank
        return journal_id, partner_id, commission_account_id, commission_analytic_id, forced_account_id, force_partner_on_bank

    def onchange_imp_config_id(self, cr, uid, ids, import_config_id, context=None):
        if not import_config_id:
            return {}
        import_config = self.pool.get("account.statement.profil").browse(cr,uid,import_config_id)
        journal_id = import_config.journal_id.id
        account_id = import_config.journal_id.default_debit_account_id.id
        credit_partner_id = import_config.partner_id and import_config.partner_id.id or False
        return {'value': {'journal_id':journal_id, 'account_id': account_id,
                    'balance_check':import_config.balance_check,
                    'credit_partner_id':credit_partner_id,
                    }}

    def credit_statement_import(self, cursor, uid, ids,
                                import_config_id,
                                file_stream,
                                ftype="csv",
                                context=None):
        "Create statement from file stream encoded in base 64"
        context = context or {}
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        attachment_obj = self.pool.get('ir.attachment')
        
        # Get variable from config
        journal_id, partner_id, commission_account_id, commission_analytic_id, \
            forced_account_id, force_partner_on_bank = self._get_value_from_import_config(cursor,uid,import_config_id)

        account_receivable, account_payable = self.get_default_accounts(cursor, uid, forced_account_id)

        ##Order of cols does not matter but first row has to be header
        keys = ['transaction_id', 'label', 'date', 'amount', 'commission_amount']
        #required_values = ['transaction_id', 'amount', 'commission_amount']
        convertion_dict = {
                            'transaction_id': unicode,
                            'label': unicode,
                            'date': datetime.datetime,
                            'amount': float,
                            'commission_amount': float
        }

        f_parser = FileParser(file_stream,
                              keys_to_validate=keys,
                              decode_base_64=True,
                              ftype=ftype)
        statement_lines = f_parser.parse()
        statement_lines = f_parser.cast_rows(statement_lines, convertion_dict)
        journal = self.pool.get('account.journal').browse(cursor, uid, journal_id)
        statement_id = statement_obj.create(cursor,
                                            uid,
                                            {   'import_config_id':import_config_id,
                                                'journal_id': journal_id,
                                                'journal_id': journal_id,
                                                'credit_partner_id': partner_id,
                                                'statement_type': 'credit_partner',
                                            },
                                            context)
        commission_global_amount = 0.0
        if not journal.default_debit_account_id \
           or not journal.default_credit_account_id:
            raise osv.except_osv(
                    _("Missing default account on journal %s")%(journal.name),
                    _("Please correct the journal"))
        try:
            for line in statement_lines:
                line_partner_id = False
                line_to_reconcile = False
                # We ensure that required values of the line are set
#                for val in required_values:
#                    if not line.get(val, False) and line.get(val, False) != 0.0:
#                        raise osv.except_osv(
#                               _("Field %s not set for line %s")%(str(line),),
#                               _("Please correct the file"))

                commission_global_amount += line.get('commission_amount', 0.0)
                values = {
                    'name': "IN %s %s"%(line['transaction_id'],
                                        line.get('label', '')),
                    'date': line.get('date', datetime.datetime.now().date()),
                    'amount': line['amount'],
                    'ref': "TID_%s"%(line['transaction_id'],),
                    'type': 'customer',
                    'statement_id': statement_id,
                    #'account_id': journal.default_debit_account_id
                }
                values['account_id'] = self._get_account_id(
                        cursor,
                        uid,
                        line['amount'],
                        account_receivable,
                        account_payable
                )
                if not line_partner_id:
                    line_partner_id = self.get_partner_from_so(cursor,
                        uid, line['transaction_id'])
                values['partner_id'] = line_partner_id
                # we finally create the line in system
                statement_line_obj.create(cursor, uid, values, context=context)

            # we create commission line
            if commission_global_amount:
                comm_values = {
                    'name': 'IN '+ _('Commission line'),
                    'date': datetime.datetime.now().date(),
                    'amount': commission_global_amount,
                    'partner_id': partner_id,
                    'type': 'general',
                    'statement_id': statement_id,
                    'account_id': commission_account_id,
                    'ref': 'commission',
                    'analytic_account_id': commission_analytic_id
                }
                statement_line_obj.create(cursor, uid,
                        comm_values, 
                        context=context)

            attachment_obj.create(
                cursor,
                uid,
                {
                    'name': 'statement file',
                    'datas': file_stream,
                    'datas_fname': "%s.%s"%(datetime.datetime.now().date(),
                                            ftype),
                    'res_model': 'account.bank.statement',
                    'res_id': statement_id,
                },
                context=context
            )
        except Exception, exc:
            logger.notifyChannel("Statement import",
                                 netsvc.LOG_ERROR,
                                 _("Statement can not be created %s") %(exc,))

            statement_obj.unlink(cursor, uid, [statement_id])
            raise exc
        return statement_id



class AccountBankSatementLine(Model):
    _inherit = "account.bank.statement.line"

    def _get_period(self, cursor, user, context=None):
        date = context.get('date', None)
        periods = self.pool.get('account.period').find(cursor, user, dt=date)
        return periods and periods[0] or False

    _columns = {
        # 'statement_id': fields.many2one('account.bank.statement', 'Statement',
        #     select=True, required=True, ondelete='cascade'),
        # 'move_ids': fields.many2many('account.move',
        #     'account_treasury_statement_line_move_rel', 'statement_line_id','move_id',
        #     'Moves'),
        'ref': fields.char('Reference', size=32, required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True),
    }
    _defaults = {
        'period_id': _get_period,
    }

    # WARNING => Crash cause the super method here calls onchange_type => and then
    # we don't call it from the good model.... => We'll need to override the complete method here
    def onchange_partner_id(self, cr, uid, ids, partner_id, import_config_id, context=None):
        # import pdb;pdb.set_trace()
        # if context is None:
        #     context = {}
        # res = super(AccountTreasurySatementLine,self).onchange_partner_id(cr, uid, ids, partner_id, context)
        # c = self.pool.get("account.statement.profil").browse(cr,uid,import_config_id)
        # acc_id=c.receivable_account_id and c.receivable_account_id.id or False
        # if acc_id:
        #     res['value'].update({'account_id':acc_id})
        # return res
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
        res_type = self.onchange_type(cr, uid, ids, partner_id, type, import_config_id, context=context)
        if res_type['value'] and res_type['value'].get('account_id', False):
            res = {'value': {'type': type, 'account_id': res_type['value']['account_id']}}
        else:
            res = {'value': {'type': type}}
                
        c = self.pool.get("account.statement.profil").browse(cr,uid,import_config_id)
        acc_id=c.receivable_account_id and c.receivable_account_id.id or False
        if acc_id:
            res['value'].update({'account_id':acc_id})
        return res
        
    # TOFIX
    def onchange_type(self, cr, uid, line_id, partner_id, type, import_config_id, context=None):
        if context is None:
            context = {}
        res = super(AccountBankSatementLine,self).onchange_type(cr, uid, line_id, partner_id, type, context)
        c = self.pool.get("account.statement.profil").browse(cr,uid,import_config_id)
        acc_id=c.receivable_account_id and c.receivable_account_id.id or False
        if acc_id:
            res['value'].update({'account_id':acc_id})
        return res

# class AccountMoveLine(Model):
#     _inherit = "account.move.line"
# 
#     _columns = {     
#         'statement_treasury_id': fields.many2one('account.bank.statement', 'Statement', help="The intermediate statement used for reconciliation", select=1),
#     }


