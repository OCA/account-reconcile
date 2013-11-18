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

    def _prepare_move_line_vals(self, cr, uid, st_line, *args, **kwargs):
        res = super(account_bank_statement, self)._prepare_move_line_vals(cr, uid, st_line, *args, **kwargs)
        period_id = self._get_period(cr, uid, st_line.statement_id.date, context=kwargs.get('context'))
        if st_line.statement_id.profile_id.one_move:
            res.update({
                'period_id': period_id,
                'date': st_line.statement_id.date,
                'name': st_line.ref,
                })
        return res


        return res

    def _prepare_move(self, cr, uid, st_line, st_line_number, context=None):
        res = super(account_bank_statement, self).\
                _prepare_move(cr, uid, st_line, st_line_number, context=context)
        res.update({
            'ref': st_line.statement_id.name,
            'name': st_line.statement_id.name,
            'date': st_line.statement_id.date,
            })
        return res

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, context):
        account_move_obj = self.pool.get('account.move')
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id

        if st.profile_id.one_move:
            if not context.get('move_id'):
                move_vals = self._prepare_move(cr, uid, st_line, st_line_number, context=context)
                context['move_id'] = account_move_obj.create(cr, uid, move_vals, context=context)
            self.create_move_line_from_st_line(cr, uid, context['move_id'], st_line_id, company_currency_id, context=context)
            return context['move_id']
        else:
            return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line_id, company_currency_id, st_line_number, context=context)
    
    def create_move_line_from_st_line(self, cr, uid, move_id, st_line_id, company_currency_id, context):
        """Create the account move line from the statement line.
           
           :param int/long move_id: ID of the account.move
           :param int/long st_line_id: ID of the account.bank.statement.line to create the move line from.
           :param int/long company_currency_id: ID of the res.currency of the company
           :return: ID of the account.move created
        """
        if context is None:
            context = {}
        res_currency_obj = self.pool.get('res.currency')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id

        context.update({'date': st_line.date})
        acc_cur = ((st_line.amount<=0) and st.journal_id.default_debit_account_id) or st_line.account_id

        context.update({
                'res.currency.compute.account': acc_cur,
            })
        amount = res_currency_obj.compute(cr, uid, st.currency.id,
                company_currency_id, st_line.amount, context=context)

        bank_move_vals = self._prepare_bank_move_line(cr, uid, st_line, move_id, amount,
            company_currency_id, context=context)
        return account_move_line_obj.create(cr, uid, bank_move_vals, context=context)

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
            super(account_bank_statement, self).button_confirm_bank(cr, uid, ids, context=context)
            if st.profile_id.one_move:
                move_id = context['move_id']
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


