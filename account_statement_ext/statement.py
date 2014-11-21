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
import openerp.addons.account.account_bank_statement as stat_mod
from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


# Monkey patch to fix bad write implementation...
def fixed_write(self, cr, uid, ids, vals, context=None):
    """ Fix performance desing of original function
    Ideally we should use a real PostgreSQL sequence or serial fields.
    I will do it when I have time."""
    res = super(stat_mod.account_bank_statement, self).write(
        cr, uid, ids, vals, context=context)
    if ids:  # will be false for an new empty bank statement
        cr.execute("UPDATE account_bank_statement_line"
                   " SET sequence = account_bank_statement_line.id + 1"
                   " where statement_id in %s", (tuple(ids),))
    return res
stat_mod.account_bank_statement.write = fixed_write


class AccountStatementProfile(orm.Model):
    """A Profile will contain all infos related to the type of
    bank statement, and related generated entries. It defines the
    journal to use, the partner and commision account and so on.
    """
    _name = "account.statement.profile"
    _inherit = ['mail.thread']
    _description = "Statement Profile"
    _order = 'sequence'

    _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer(
            'Sequence',
            help="Gives a sequence in lists, the first profile will be used "
                 "as default"),
        'partner_id': fields.many2one(
            'res.partner',
            'Bank/Payment Office partner',
            help="Put a partner if you want to have it on the commission move "
                 "(and optionaly on the counterpart of the intermediate/"
                 "banking move if you tick the corresponding checkbox)."),
        'journal_id': fields.many2one(
            'account.journal',
            'Financial journal to use for transaction',
            required=True),
        'commission_account_id': fields.many2one(
            'account.account',
            'Commission account',
            required=True),
        'commission_analytic_id': fields.many2one(
            'account.analytic.account',
            'Commission analytic account'),
        'receivable_account_id': fields.many2one(
            'account.account',
            'Force Receivable/Payable Account',
            help="Choose a receivable account to force the default "
                 "debit/credit account (eg. an intermediat bank account "
                 "instead of default debitors)."),
        'force_partner_on_bank': fields.boolean(
            'Force partner on bank move',
            help="Tick that box if you want to use the credit "
                 "institute partner in the counterpart of the "
                 "intermediate/banking move."),
        'balance_check': fields.boolean(
            'Balance check',
            help="Tick that box if you want OpenERP to control "
                 "the start/end balance before confirming a bank statement. "
                 "If don't ticked, no balance control will be done."),
        'bank_statement_prefix': fields.char('Bank Statement Prefix', size=32),
        'bank_statement_ids': fields.one2many('account.bank.statement',
                                              'profile_id',
                                              'Bank Statement Imported'),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    def _check_partner(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.partner_id is False and obj.force_partner_on_bank:
            return False
        return True

    _constraints = [
        (_check_partner,
         "You need to put a partner if you tic the 'Force partner on bank "
         "move'!", []),
    ]

    _sql_constraints = [
        ('name_uniq', 'unique (name, company_id)',
         'The name of the bank statement must be unique !')
    ]


class AccountBankStatement(orm.Model):
    """We improve the bank statement class mostly for :
    - Removing the period and compute it from the date of each line.
    - Allow to remove the balance check depending on the chosen profile
    - Report errors on confirmation all at once instead of crashing onr by one
    - Add a profile notion that can change the generated entries on statement
      confirmation.
     For this, we had to override quite some long method and we'll need to
     maintain them up to date. Changes are point up by '#Chg' comment.
     """

    _inherit = "account.bank.statement"

    def _default_period(self, cr, uid, context=None):
        """Statement default period"""
        if context is None:
            context = {}
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(
            cr, uid, dt=context.get('date'), context=context)
        return periods and periods[0] or False

    def _default_profile(self, cr, uid, context=None):
        """Returns the default statement profile
        Default profile is the one with the lowest sequence of user's company

        :return profile_id or False
        """
        user_obj = self.pool['res.users']
        profile_obj = self.pool['account.statement.profile']
        user = user_obj.browse(cr, uid, uid, context=context)
        profile_ids = profile_obj.search(
            cr, uid, [('company_id', '=', user.company_id.id)], context=context
        )
        return profile_ids[0] if profile_ids else False

    def _get_statement_from_profile(self, cr, uid, profile_ids, context=None):
        """Stored function field trigger.

        Weirdness warning: we are in the class account.bank.statement, but
        when the ORM calls this, self is an account.statement.profile.

        Returns a list of account.bank.statement ids to recompute.
        """
        triggered = []
        for profile in self.browse(cr, uid, profile_ids, context=context):
            triggered += [st.id for st in profile.bank_statement_ids]
        return triggered

    def _us(self, cr, uid, ids, context=None):
        return ids

    _columns = {
        'profile_id': fields.many2one(
            'account.statement.profile',
            'Bank Account Profile',
            required=True,
            states={'draft': [('readonly', False)]}),
        'credit_partner_id': fields.related(
            'profile_id',
            'partner_id',
            type='many2one',
            relation='res.partner',
            string='Financial Partner',
            store={
                'account.bank.statement': (_us, ['profile_id'], 10),
                'account.statement.profile': (
                    _get_statement_from_profile, ['partner_id'], 10),
            },
            readonly=True),
        'balance_check': fields.related(
            'profile_id',
            'balance_check',
            type='boolean',
            string='Balance check',
            store={
                'account.bank.statement': (_us, ['profile_id'], 10),
                'account.statement.profile': (
                    _get_statement_from_profile, ['balance_check'], 10),
            },
            readonly=True
        ),
        'journal_id': fields.related(
            'profile_id',
            'journal_id',
            type='many2one',
            relation='account.journal',
            string='Journal',
            store={
                'account.bank.statement': (_us, ['profile_id'], 10),
                'account.statement.profile': (
                    _get_statement_from_profile, ['journal_id'], 10),
            },
            readonly=True),
        'period_id': fields.many2one(
            'account.period',
            'Period',
            required=False,
            readonly=False,
            invisible=True),
    }

    _defaults = {
        'period_id': _default_period,
        'profile_id': _default_profile,
    }

    def create(self, cr, uid, vals, context=None):
        """Need to pass the journal_id in vals anytime because of
        account.cash.statement need it."""
        if 'profile_id' in vals:
            profile_obj = self.pool['account.statement.profile']
            profile = profile_obj.browse(
                cr, uid, vals['profile_id'], context=context)
            vals['journal_id'] = profile.journal_id.id
        return super(AccountBankStatement, self).create(
            cr, uid, vals, context=context)

    def _get_period(self, cr, uid, date, context=None):
        """Return matching period for a date."""
        if context is None:
            context = {}
        period_obj = self.pool['account.period']
        local_context = context.copy()
        local_context['account_period_prefer_normal'] = True
        periods = period_obj.find(cr, uid, dt=date, context=local_context)
        return periods and periods[0] or False

    def _check_company_id(self, cr, uid, ids, context=None):
        """Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line
        """
        for statement in self.browse(cr, uid, ids, context=context):
            # statement.company_id is a related store=True that for some
            # reason doesn't work in YAML tests. As a workaround, I unwind it
            # to statement.journal_id.company_id here.
            if (statement.period_id and
                    statement.journal_id.company_id.id !=
                    statement.period_id.company_id.id):
                return False
            for line in statement.line_ids:
                if (line.period_id and
                        statement.journal_id.company_id.id
                        != line.period_id.company_id.id):
                    return False
        return True

    _constraints = [
        (_check_company_id,
         'The journal and period chosen have to belong to the same company.',
         ['journal_id', 'period_id']),
    ]

    def _prepare_move(self, cr, uid, st_line, st_line_number, context=None):
        """Add the period_id from the statement line date to the move
        preparation. Originaly, it was taken from the statement period_id
           :param browse_record st_line: account.bank.statement.line record
             to create the move from.
           :param char st_line_number: will be used as the name of the
             generated account move
           :return: dict of value to create() the account.move
        """
        if context is None:
            context = {}
        res = super(AccountBankStatement, self)._prepare_move(
            cr, uid, st_line, st_line_number, context=context)
        ctx = context.copy()
        ctx['company_id'] = st_line.company_id.id
        period_id = self._get_period(cr, uid, st_line.date, context=ctx)
        res.update({'period_id': period_id})
        return res

    def _prepare_move_line_vals(
            self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, analytic_id=False,
            partner_id=False, context=None):
        """Add the period_id from the statement line date to the move
        preparation. Originaly, it was taken from the statement period_id

           :param browse_record st_line: account.bank.statement.line record
             to create the move from.
           :param int/long move_id: ID of the account.move to link the move
             line
           :param float debit: debit amount of the move line
           :param float credit: credit amount of the move line
           :param int/long currency_id: ID of currency of the move line to
             create
           :param float amount_currency: amount of the debit/credit expressed
             in the currency_id
           :param int/long account_id: ID of the account to use in the move
             line if different from the statement line account ID
           :param int/long analytic_id: ID of analytic account to put on the
             move line
           :param int/long partner_id: ID of the partner to put on the move
             line
           :return: dict of value to create() the account.move.line
        """
        if context is None:
            context = {}
        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            cr, uid, st_line, move_id, debit, credit,
            currency_id=currency_id,
            amount_currency=amount_currency,
            account_id=account_id,
            analytic_id=analytic_id,
            partner_id=partner_id, context=context)
        ctx = context.copy()
        ctx['company_id'] = st_line.company_id.id
        period_id = self._get_period(cr, uid, st_line.date, context=ctx)
        res.update({'period_id': period_id})
        return res

    def _get_counter_part_partner(self, cr, uid, st_line, context=None):
        """We change the move line generated from the lines depending on the
        profile:
          - If partner_id is set and force_partner_on_bank is ticked, we'll let
          the partner of each line for the debit line, but we'll change it on
          the credit move line for the choosen partner_id
          => This will ease the reconciliation process with the bank as the
          partner will match the bank statement line
        :param browse_record st_line: account.bank.statement.line record to
          create the move from.
        :return: int/long of the res.partner to use as counterpart
        """
        bank_partner_id = super(AccountBankStatement, self
                                )._get_counter_part_partner(cr, uid, st_line,
                                                            context=context)
        # get the right partner according to the chosen profile
        if st_line.statement_id.profile_id.force_partner_on_bank:
            bank_partner_id = st_line.statement_id.profile_id.partner_id.id
        return bank_partner_id

    def _get_st_number_period_profile(self, cr, uid, date, profile_id):
        """Retrieve the name of bank statement from sequence, according to the
        period corresponding to the date passed in args. Add a prefix if set in
        the profile.

        :param: date: date of the statement used to compute the right period
        :param: int/long: profile_id: the account.statement.profile ID from
          which to take the bank_statement_prefix for the name
        :return: char: name of the bank statement (st_number)
        """
        year = self.pool['account.period'].browse(
            cr, uid, self._get_period(cr, uid, date)).fiscalyear_id.id
        profile = self.pool.get(
            'account.statement.profile').browse(cr, uid, profile_id)
        c = {'fiscalyear_id': year}
        obj_seq = self.pool['ir.sequence']
        journal_sequence_id = (profile.journal_id.sequence_id and
                               profile.journal_id.sequence_id.id or False)
        if journal_sequence_id:
            st_number = obj_seq.next_by_id(
                cr, uid, journal_sequence_id, context=c)
        else:
            st_number = obj_seq.next_by_code(
                cr, uid, 'account.bank.statement', context=c)
        if profile.bank_statement_prefix:
            st_number = profile.bank_statement_prefix + st_number
        return st_number

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """Completely override the method in order to have an error message
        which displays all the messages instead of having them pop one by one.
        We have to copy paste a big block of code, changing the error stack +
        managing period from date.

        TODO: Log the error in a bank statement field instead of using a popup!
        """
        for st in self.browse(cr, uid, ids, context=context):

            j_type = st.journal_id.type
            company_currency_id = st.journal_id.company_id.currency_id.id
            if not self.check_status_condition(cr, uid, st.state,
                                               journal_type=j_type):
                continue
            self.balance_check(
                cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise orm.except_orm(
                    _('Configuration Error!'),
                    _('Please verify that an account is defined in the '
                      'journal.'))
            if not st.name == '/':
                st_number = st.name
            else:
                # Begin Changes
                st_number = self._get_st_number_period_profile(
                    cr, uid, st.date, st.profile_id.id)
            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise orm.except_orm(
                        _('Error!'),
                        _('The account entries lines are not in valid state.'))
            errors_stack = []
            for st_line in st.line_ids:
                try:
                    if st_line.analytic_account_id:
                        if not st.journal_id.analytic_journal_id:
                            raise orm.except_orm(
                                _('No Analytic Journal!'),
                                _("You have to assign an analytic journal on "
                                  "the '%s' journal!") % st.journal_id.name)
                    if not st_line.amount:
                        continue
                    st_line_number = self.get_next_st_line_number(
                        cr, uid, st_number, st_line, context)
                    self.create_move_from_st_line(
                        cr, uid, st_line.id, company_currency_id,
                        st_line_number, context)
                except (orm.except_orm, osv.except_osv) as exc:
                    msg = "Line ID %s with ref %s had following error: %s" % (
                        st_line.id, st_line.ref, exc.value)
                    errors_stack.append(msg)
                except Exception, exc:
                    msg = "Line ID %s with ref %s had following error: %s" % (
                        st_line.id, st_line.ref, str(exc))
                    errors_stack.append(msg)
            if errors_stack:
                msg = u"\n".join(errors_stack)
                raise orm.except_orm(_('Error'), msg)
            self.write(cr, uid, [st.id],
                       {'name': st_number,
                        'balance_end_real': st.balance_end},
                       context=context)
            body = _('Statement %s confirmed, journal items were '
                     'created.') % st_number
            self.message_post(cr, uid, [st.id],
                              body,
                              context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def get_account_for_counterpart(self, cr, uid, amount, account_receivable,
                                    account_payable):
        """For backward compatibility."""
        account_id, account_type = self.get_account_and_type_for_counterpart(
            cr, uid, amount, account_receivable, account_payable)
        return account_id

    def _compute_type_from_partner_profile(self, cr, uid, partner_id,
                                           default_type, context=None):
        """Compute the statement line type
           from partner profile (customer, supplier)"""
        obj_partner = self.pool['res.partner']
        part = obj_partner.browse(cr, uid, partner_id, context=context)
        if part.supplier == part.customer:
            return default_type
        if part.supplier:
            return 'supplier'
        else:
            return 'customer'

    def _compute_type_from_amount(self, cr, uid, amount):
        """Compute the statement type based on amount"""
        if amount in (None, False):
            return 'general'
        if amount < 0:
            return 'supplier'
        return 'customer'

    def get_type_for_counterpart(self, cr, uid, amount, partner_id=False):
        """Give the amount and receive the type to use for the line.
        The rules are:
         - If the customer checkbox is checked on the found partner, type
         customer
         - If the supplier checkbox is checked on the found partner, typewill
         be supplier
         - If both checkbox are checked or none of them, it'll be based on the
         amount:
              If amount is positif the type customer,
              If amount is negativ, the type supplier
        :param float: amount of the line
        :param int/long: partner_id the partner id
        :return: type as string: the default type to use: 'customer' or
          'supplier'.
        """
        s_line_type = self._compute_type_from_amount(cr, uid, amount)
        if partner_id:
            s_line_type = self._compute_type_from_partner_profile(
                cr, uid, partner_id, s_line_type)
        return s_line_type

    def get_account_and_type_for_counterpart(
            self, cr, uid, amount, account_receivable, account_payable,
            partner_id=False):
        """
        Give the amount, payable and receivable account (that can be found
        using get_default_pay_receiv_accounts method) and receive the one to
        use. This method should be use when there is no other way to know which
        one to take. The rules are:
         - If the customer checkbox is checked on the found partner, type and
         account will be customer and receivable
         - If the supplier checkbox is checked on the found partner, type and
         account will be supplier and payable
         - If both checkbox are checked or none of them, it'll be based on the
         amount:
              If amount is positive, the type and account will be customer and
              receivable,
              If amount is negative, the type and account will be supplier and
              payable
        Note that we return the payable or receivable account from agrs and not
        from the optional partner_id given!

        :param float: amount of the line
        :param int/long: account_receivable the  receivable account
        :param int/long: account_payable the payable account
        :param int/long: partner_id the partner id
        :return: dict with [account_id as int/long,type as string]: the
          default account to be used by statement line as the counterpart of
          the journal account depending on the amount and the type as
          'customer' or 'supplier'.
        """
        account_id = False
        ltype = self.get_type_for_counterpart(
            cr, uid, amount, partner_id=partner_id)
        if ltype == 'supplier':
            account_id = account_payable
        else:
            account_id = account_receivable
        if not account_id:
            raise orm.except_orm(
                _('Can not determine account'),
                _('Please ensure that minimal properties are set'))
        return [account_id, ltype]

    def get_default_pay_receiv_accounts(self, cr, uid, context=None):
        """
        We try to determine default payable/receivable accounts to be used as
        counterpart from the company default propoerty. This is to be used if
        there is no otherway to find the good one, or to find a default value
        that will be overriden by a completion method (rules of
        account_statement_base_completion) afterwards.

        :return: tuple of int/long ID that give account_receivable,
        account_payable based on company default.
        """
        property_obj = self.pool['ir.property']
        account_receivable = property_obj.get(
            cr, uid, 'property_account_receivable', 'res.partner',
            context=context)
        account_payable = property_obj.get(cr, uid, 'property_account_payable',
                                           'res.partner', context=context)

        return (account_receivable and account_receivable.id or False,
                account_payable and account_payable.id or False)

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        """
        Balance check depends on the profile. If no check for this profile is
        required, return True and do nothing, otherwise call super.

        :param int/long st_id: ID of the concerned account.bank.statement
        :param char: journal_type that concern the bank statement
        :return: True
        """
        st = self.browse(cr, uid, st_id, context=context)
        if st.balance_check:
            return super(AccountBankStatement, self
                         ).balance_check(cr, uid, st_id, journal_type,
                                         context=context)
        else:
            return True

    def onchange_imp_config_id(self, cr, uid, ids, profile_id, context=None):
        """Compute values on the change of the profile.

        :param: int/long: profile_id that changed
        :return dict of dict with key = name of the field
        """
        if not profile_id:
            return {}
        import_config = self.pool["account.statement.profile"].browse(
            cr, uid, profile_id, context=context)
        journal_id = import_config.journal_id.id
        return {'value': {'journal_id': journal_id,
                          'balance_check': import_config.balance_check}}


class AccountBankStatementLine(orm.Model):
    """Override to compute the period from the date of the line, add a method
    to retrieve the values for a line from the profile. Override the on_change
    method to take care of the profile when fullfilling the bank statement
    manually. Set the reference to 64 Char long instead 32.
    """
    _inherit = "account.bank.statement.line"

    def _get_period(self, cr, uid, context=None):
        """Return matching period for a date."""
        if context is None:
            context = {}
        period_obj = self.pool['account.period']
        date = context.get('date')
        local_context = context.copy()
        local_context['account_period_prefer_normal'] = True
        try:
            periods = period_obj.find(cr, uid, dt=date, context=local_context)
        except (orm.except_orm, osv.except_osv):
            # if no period defined, we are certainly at installation time
            return False
        return periods and periods[0] or False

    def _get_default_account(self, cr, uid, context=None):
        return self.get_values_for_line(cr, uid, context=context)['account_id']

    _columns = {
        # Set them as required + 64 char instead of 32
        'ref': fields.char('Reference', size=64, required=True),
        'period_id': fields.many2one(
            'account.period', 'Period', required=True),
    }
    _defaults = {
        'period_id': _get_period,
        'account_id': _get_default_account,
    }

    def get_values_for_line(self, cr, uid, profile_id=False, partner_id=False,
                            line_type=False, amount=False,
                            master_account_id=None, context=None):
        """Return the account_id to be used in the line of a bank statement.
        It'll base the result as follow:
            - If a receivable_account_id is set in the profile, return this
            value and type = general
            # TODO
            - Elif how_get_type_account is set to force_supplier or
            force_customer, will take respectively payable and type=supplier,
              receivable and type=customer otherwise
            # END TODO
            - Elif line_type is given, take the partner receivable/payable
            property (payable if type=supplier, receivable otherwise)
            - Elif amount is given:
                 - If the customer checkbox is checked on the found partner,
                 type and account will be customer and receivable
                 - If the supplier checkbox is checked on the found partner,
                 type and account will be supplier and payable
                 - If both checkbox are checked or none of them, it'll be based
                 on the amount :
                      If amount is positive, the type and account will be
                      customer and receivable,
                      If amount is negative, the type and account will be
                      supplier an payable
            - Then, if no partner are given we look and take the property from
            the company so we always give a value for account_id. Note that in
            that case, we return the receivable one.
        :param int/long profile_id of the related bank statement
        :param int/long partner_id of the line
        :param char line_type: a value from: 'general', 'supplier', 'customer'
        :param float: amount of the line
        :return: A dict of value that can be passed directly to the write
          method of the statement line:
                     {'partner_id': value,
                      'account_id' : value,
                      'type' : value,
                       ...
                     }
        """
        res = {}
        obj_partner = self.pool.get('res.partner')
        obj_stat = self.pool.get('account.bank.statement')
        receiv_account = pay_account = account_id = False
        # If profile has a receivable_account_id, we return it in any case
        if master_account_id:
            res['account_id'] = master_account_id
            # We return general as default instead of get_type_for_counterpart
            # for perfomance reasons as line_type is not a meaningfull value
            # as account is forced
            res['type'] = line_type if line_type else 'general'
            return res
        # To optimize we consider passing false means there is no account
        # on profile
        if profile_id and master_account_id is None:
            profile = self.pool.get("account.statement.profile").browse(
                cr, uid, profile_id, context=context)
            if profile.receivable_account_id:
                res['account_id'] = profile.receivable_account_id.id
                # We return general as default instead of
                # get_type_for_counterpart for perfomance reasons as line_type
                # is not a meaningfull value as account is forced
                res['type'] = line_type if line_type else 'general'
                return res
        # If no account is available on profile you have to do the lookup
        # This can be quite a performance killer as we read ir.properity fields
        if partner_id:
            part = obj_partner.browse(cr, uid, partner_id, context=context)
            part = part.commercial_partner_id
            # When the method is called from bank statement completion,
            # ensure that the line's partner is a commercial
            # (accounting) entity
            res['partner_id'] = part.id
            pay_account = part.property_account_payable.id
            receiv_account = part.property_account_receivable.id
        # If no value, look on the default company property
        if not pay_account or not receiv_account:
            receiv_account, pay_account = obj_stat.\
                get_default_pay_receiv_accounts(cr, uid, context=None)
        account_id, comp_line_type = obj_stat.\
            get_account_and_type_for_counterpart(
                cr, uid, amount, receiv_account, pay_account,
                partner_id=partner_id)
        res['account_id'] = account_id if account_id else receiv_account
        res['type'] = line_type if line_type else comp_line_type
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, profile_id=None,
                            context=None):
        """
        Override of the basic method as we need to pass the profile_id in the
        on_change_type call.
        Moreover, we now call the get_account_and_type_for_counterpart method
        now to get the type to use.
        """
        obj_stat = self.pool['account.bank.statement']
        if not partner_id:
            return {}
        line_type = obj_stat.get_type_for_counterpart(
            cr, uid, 0.0, partner_id=partner_id)
        res_type = self.onchange_type(
            cr, uid, ids, partner_id, line_type, profile_id, context=context)
        if res_type['value'] and res_type['value'].get('account_id', False):
            return {'value': {'type': line_type,
                              'account_id': res_type['value']['account_id'],
                              'voucher_id': False}}
        return {'value': {'type': line_type}}

    def onchange_type(self, cr, uid, line_id, partner_id, line_type,
                      profile_id, context=None):
        """Keep the same features as in standard and call super. If an account
        is returned, call the method to compute line values.
        """
        res = super(AccountBankStatementLine, self
                    ).onchange_type(cr, uid, line_id, partner_id,
                                    line_type, context=context)
        if 'account_id' in res['value']:
            result = self.get_values_for_line(cr, uid,
                                              profile_id=profile_id,
                                              partner_id=partner_id,
                                              line_type=line_type,
                                              context=context)
            if result:
                res['value'].update({'account_id': result['account_id']})
        return res
