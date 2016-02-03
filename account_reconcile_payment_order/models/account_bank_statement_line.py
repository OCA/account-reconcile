# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from decimal import Decimal
from openerp import models, api
from openerp.tools.float_utils import float_repr


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.model
    def get_possible_payment_orders_for_statement_line(self, this):
        """find orders that might be candidates for matching a statement
        line"""
        digits = self.env['decimal.precision'].precision_get('Account')
        self.env.cr.execute(
            '''with order_sums as (
                select order_id, sum(amount_currency) as amount
                from payment_line
                join payment_order o on o.id=order_id
                where o.state in ('sent', 'done')
                group by order_id)
            select order_id from order_sums where amount = %s''',
            (Decimal(float_repr(abs(this.amount), digits)),))
        order_ids = [i for i, in self.env.cr.fetchall()]
        # verify that this ids are accessible to the user
        domain = [
            ('id', 'in', order_ids),
        ]
        return self.env['payment.order'].search(domain)

    @api.model
    def get_reconcile_lines_from_order(self, this, orders, excluded_ids=None):
        """return lines to reconcile our statement line with"""
        order = orders[0]
        if order.state == 'sent':
            move_lines_list = list(set(order._get_transfer_move_lines()))
        else:
            move_lines = order.line_ids.mapped('move_line_id').filtered(
                lambda x: not x.reconcile_id)
            move_lines_list = [x for x in move_lines]
        return self.env['account.move.line']\
            .prepare_move_lines_for_reconciliation_widget(move_lines_list)

    @api.model
    def get_reconciliation_proposition(self, this, excluded_ids=None):
        """See if we find a set payment order that matches our line. If yes,
        return all unreconciled lines from there"""
        orders = self.get_possible_payment_orders_for_statement_line(this)
        if orders:
            reconcile_lines = self.get_reconcile_lines_from_order(
                this, orders, excluded_ids=None)
            if reconcile_lines:
                return reconcile_lines
        return super(AccountBankStatementLine, self)\
            .get_reconciliation_proposition(this, excluded_ids=excluded_ids)
