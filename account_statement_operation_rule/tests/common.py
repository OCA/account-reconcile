# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


def prepare_statement(test, difference,
                      statement_line_currency=None,
                      move_line_currency=None,
                      amount_currency_difference=0):
    """ Prepare a bank statement line and a move line

    The difference is applied on the bank statement line relatively to
    the move line.
    """
    amount = 100
    amount_currency = 120
    statement_obj = test.env['account.bank.statement']
    statement_line_obj = test.env['account.bank.statement.line']
    move_obj = test.env['account.move']
    move_line_obj = test.env['account.move.line']
    statement = statement_obj.create({
        'name': '/',
        'journal_id': test.ref('account.cash_journal')
    })
    line_vals = {
        'name': '001',
        'amount': amount + difference,
        'statement_id': statement.id,
    }
    if statement_line_currency:
        line_vals.update({
            'currency_id': statement_line_currency.id,
            'amount_currency': amount_currency + amount_currency_difference,
        })

    statement_line = statement_line_obj.create(line_vals)
    move = move_obj.create({
        'journal_id': test.ref('account.sales_journal')
    })
    line_vals = {
        'move_id': move.id,
        'name': '001',
        'account_id': test.ref('account.a_recv'),
        'debit': amount,
    }
    if move_line_currency:
        line_vals.update({
            'currency_id': move_line_currency.id,
            'amount_currency': amount_currency,
        })
    move_line = move_line_obj.create(line_vals)
    line_vals = {
        'move_id': move.id,
        'name': '001',
        'account_id': test.ref('account.a_sale'),
        'credit': amount,
    }
    if move_line_currency:
        line_vals['currency_id'] = move_line_currency.id
    move_line_obj.create(line_vals)
    return statement_line, move_line
