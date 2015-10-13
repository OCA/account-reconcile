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

from openerp.osv import fields, orm


class AccountStatementProfile(orm.Model):
    _inherit = "account.statement.profile"
    _columns = {
        'one_move': fields.boolean(
            'Group Journal Items',
            help="Only one Journal Entry will be generated on the "
                 "validation of the bank statement."),
        'split_transfer_line': fields.boolean(
            'Split Transfer Line',
            help="Two transfer lines will be automatically generated : one "
                 "for the refunds and one for the payments.")
    }


class AccountBankStatement(orm.Model):
    _inherit = "account.bank.statement"

    def _prepare_move_line_vals(self, cr, uid, st_line, *args, **kwargs):
        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            cr, uid, st_line, *args, **kwargs)
        period_id = self._get_period(cr, uid, st_line.statement_id.date,
                                     context=kwargs.get('context'))
        if st_line.statement_id.profile_id.one_move:
            res.update({
                'period_id': period_id,
                'date': st_line.statement_id.date,
                'name': st_line.ref,
            })
        return res

    def _prepare_move(self, cr, uid, st_line, st_line_number, context=None):
        res = super(AccountBankStatement, self).\
            _prepare_move(cr, uid, st_line, st_line_number, context=context)
        res.update({
            'ref': st_line.statement_id.name,
            'name': st_line.statement_id.name,
            'date': st_line.statement_id.date,
        })
        return res

    def create_move_from_st_line(self, cr, uid, st_line_id,
                                 company_currency_id,
                                 st_line_number, context=None):
        if context is None:
            context = {}
        # For compability with module account_constraints
        context['from_parent_object'] = True
        account_move_obj = self.pool['account.move']
        st_line_obj = self.pool['account.bank.statement.line']
        st_line = st_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id
        if st.profile_id.one_move:
            if not context.get('move_id'):
                move_vals = self._prepare_move(
                    cr, uid, st_line, st_line_number, context=context)
                context['move_id'] = account_move_obj.create(
                    cr, uid, move_vals, context=context)
            self.create_move_line_from_st_line(cr, uid, context['move_id'],
                                               st_line_id, company_currency_id,
                                               context=context)
            return context['move_id']
        else:
            return super(AccountBankStatement, self).create_move_from_st_line(
                cr, uid, st_line_id, company_currency_id, st_line_number,
                context=context)

    def create_move_line_from_st_line(self, cr, uid, move_id, st_line_id,
                                      company_currency_id, context=None):
        """Create the account move line from the statement line.

        :param int/long move_id: ID of the account.move
        :param int/long st_line_id: ID of the account.bank.statement.line
          to create the move line from.
        :param int/long company_currency_id: ID of the res.currency of the
          company
        :return: ID of the account.move created
        """
        if context is None:
            context = {}
        res_currency_obj = self.pool['res.currency']
        account_move_line_obj = self.pool['account.move.line']
        st_line_obj = self.pool['account.bank.statement.line']
        st_line = st_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id
        context.update({'date': st_line.date})
        acc_cur = (((st_line.amount <= 0)
                    and st.journal_id.default_debit_account_id) or
                   st_line.account_id)
        context.update({
            'res.currency.compute.account': acc_cur,
        })
        amount = res_currency_obj.compute(
            cr, uid, st.currency.id, company_currency_id, st_line.amount,
            context=context)
        bank_move_vals = self._prepare_bank_move_line(
            cr, uid, st_line, move_id, amount, company_currency_id,
            context=context)
        return account_move_line_obj.create(cr, uid, bank_move_vals,
                                            context=context)

    def _valid_move(self, cr, uid, move_id, context=None):
        move_obj = self.pool['account.move']
        move_obj.post(cr, uid, [move_id], context=context)
        return True

    def _prepare_transfer_move_line_vals(self, cr, uid, st, name, amount,
                                         move_id, context=None):
        """Prepare the dict of values to create the transfer move lines."""
        account_id = st.profile_id.journal_id.default_debit_account_id.id
        if amount < 0.0:
            debit = 0.0
            credit = -amount
        else:
            debit = amount
            credit = 0.0
        vals = {
            'name': name,
            'date': st.date,
            'partner_id': st.profile_id.partner_id.id,
            'statement_id': st.id,
            'account_id': account_id,
            'ref': name,
            'move_id': move_id,
            'credit': credit,
            'debit': debit,
            'journal_id': st.journal_id.id,
            'period_id': st.period_id.id,
        }
        return vals

    def create_move_transfer_lines(self, cr, uid, move, st, context=None):
        move_line_obj = self.pool['account.move.line']
        move_id = move.id
        refund = 0.0
        payment = 0.0
        transfer_lines = []
        transfer_line_ids = []
        # Calculate the part of the refund amount and the payment amount
        for move_line in move.line_id:
            refund -= move_line.debit
            payment += move_line.credit
        # Create 2 Transfer lines or One global tranfer line
        if st.profile_id.split_transfer_line:
            if refund:
                transfer_lines.append(['Refund Transfer', refund])
            if payment:
                transfer_lines.append(['Payment Transfer', payment])
        else:
            amount = payment + refund
            if amount:
                transfer_lines.append(['Transfer', amount])
        for transfer_line in transfer_lines:
            vals = self._prepare_transfer_move_line_vals(
                cr, uid, st, transfer_line[0], transfer_line[1], move_id,
                context=context)
            transfer_line_ids.append(
                move_line_obj.create(cr, uid, vals, context=context))
        return transfer_line_ids

    def button_confirm_bank(self, cr, uid, ids, context=None):
        st_line_obj = self.pool['account.bank.statement.line']
        if context is None:
            context = {}
        for st in self.browse(cr, uid, ids, context=context):
            super(AccountBankStatement, self).button_confirm_bank(
                cr, uid, ids, context=context)
            if st.profile_id.one_move and context.get('move_id', False):
                move_id = context['move_id']
                self._valid_move(cr, uid, move_id, context=context)
                lines_ids = [x.id for x in st.line_ids]
                st_line_obj.write(cr, uid, lines_ids,
                                  {'move_ids': [(4, move_id, False)]},
                                  context=context)
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        for st in self.browse(cr, uid, ids, context=context):
            if st.profile_id.one_move and st.line_ids:
                for move in st.line_ids[0].move_ids:
                    if move.state != 'draft':
                        move.button_cancel(context=context)
                    move.unlink(context=context)
                st.write({'state': 'draft'}, context=context)
            else:
                super(AccountBankStatement, self).button_cancel(
                    cr, uid, ids, context=context)
        return True
