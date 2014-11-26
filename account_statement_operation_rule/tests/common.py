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


def prepare_statement(test, difference):
    """ Prepare a bank statement line and a move line

    The difference is applied on the bank statement line relatively to
    the move line.
    """
    amount = 100
    statement_obj = test.env['account.bank.statement']
    statement_line_obj = test.env['account.bank.statement.line']
    move_obj = test.env['account.move']
    move_line_obj = test.env['account.move.line']
    statement = statement_obj.create({
        'name': '/',
        'journal_id': test.ref('account.cash_journal')
    })
    statement_line = statement_line_obj.create({
        'name': '001',
        'amount': amount + difference,
        'statement_id': statement.id,
    })
    move = move_obj.create({
        'journal_id': test.ref('account.sales_journal')
    })
    move_line = move_line_obj.create({
        'move_id': move.id,
        'name': '001',
        'account_id': test.ref('account.a_recv'),
        'debit': amount,
    })
    move_line_obj.create({
        'move_id': move.id,
        'name': '001',
        'account_id': test.ref('account.a_sale'),
        'credit': amount,
    })
    return statement_line, move_line
