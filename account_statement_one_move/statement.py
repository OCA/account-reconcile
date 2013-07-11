# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_one_move for OpenERP
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm, osv



class AccountStatementProfil(orm.Model):
    _inherit = "account.statement.profile"   
    _columns = {
       'one_move': fields.boolean('One Move', 
                help="Tic that box if you want OpenERP to generated only"
                "one move when the bank statement is validated")
    }


class account_bank_statement(orm.Model):
    _inherit = "account.bank.statement"

    ##################### START UGLY COPY/PASTE
    #REALLY SORRY for the ugly code but the module bank statement should be re-written
    #It is impossible to overwrite it correctly
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
        
        if context.get('move_id'):                  #Chg2
            move_id = context['move_id']            #Chg2
        else:                                       #Chg2
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

        if context['move_id']:                   #Chg2
            return move_id                       #Chg2

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



    ####################### END OF UGLY COPY/PASTE
    
    def _prepare_move(self, cr, uid, st, context=None):
        period_id = st.period_id or self._get_period(
            cr, uid, st.date, context=context) 
        return {
            'journal_id': st.journal_id.id,
            'period_id': period_id,
            'date': st.date,
            'name': st.name,
            'ref': st.name,
        }
    
    def _create_move(self, cr, uid, st, context=None):
        move_obj = self.pool.get('account.move')
        move_vals = self._prepare_move(cr, uid, st, context=context)
        return move_obj.create(cr, uid, move_vals, context=context)
   
    def _valid_move(self, cr, uid, move_id, context=None):
        move_obj = self.pool.get('account.move')
        move = move_obj.browse(cr, uid, move_id, context=context)
        move_obj.post(cr, uid, [move_id], context=context)
        return True

    def button_confirm_bank(self, cr, uid, ids, context=None):
        st_line_obj = self.pool.get('account.bank.statement.line')
        if context is None:
            context = {}
        for st in self.browse(cr, uid, ids, context=context):
            if st.profile_id.one_move:
                move_id = self._create_move(cr, uid, st, context=context)
                context['move_id'] = move_id
            super(account_bank_statement, self).button_confirm_bank(cr, uid, ids, context=context)
            if st.profile_id.one_move:
                self._valid_move(cr, uid, move_id, context=context)
                lines_ids = [x.id for x in st.line_ids]
                st_line_obj.write(cr, uid, lines_ids,
                        {'move_ids': [(4, move_id, False)]},
                        context=context)
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        done = []
        for st in self.browse(cr, uid, ids, context=context):
            if st.profile_id.one_move:
                for move in st.line_ids[0].move_ids:
                    if move.state <> 'draft':
                        move.button_cancel(context=context)
                    move.unlink(context=context)
                st.write({'state':'draft'}, context=context)
            else:
                super(account_bank_statement, self).button_cancel(cr, uid, ids, context=context)
       return True


