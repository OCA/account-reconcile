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

from openerp.tests import common
from openerp.addons.account_statement_operation_rule.tests.common import (
    prepare_statement
)


def prepare_statement_with_dunning_fees(test, difference, fees):
    """ Prepare a bank statement line and a move line

    The difference is applied on the bank statement line relatively to
    the move line.

    The fees is a list of dunning fees (amounts) applied on the move line.
    """
    statement_line, move_line = prepare_statement(test, difference)
    control_lines = test.env['credit.control.line'].browse()
    for fee in fees:
        values = {
            'date': move_line.date,
            'date_due': move_line.date,
            'state': 'sent',
            'channel': 'letter',
            'partner_id': test.ref('base.res_partner_1'),
            'amount_due': move_line.credit,
            'balance_due': move_line.credit,
            'policy_level_id': test.ref('account_credit_control.3_time_1'),
            'company_id': move_line.company_id.id,
            'move_line_id': move_line.id,
            'dunning_fees_amount': fee,
        }
        control_lines += test.env['credit.control.line'].create(values)
    return statement_line, move_line, control_lines


class TestDunningRule(common.TransactionCase):

    def setUp(self):
        super(TestDunningRule, self).setUp()
        self.operation_obj = self.env['account.statement.operation.template']
        self.rule_obj = self.env['account.statement.operation.rule']
        self.operation_dunning = self.operation_obj.create({
            'name': 'Dunning Fees',
            'label': 'Dunning Fees',
            'account_id': self.ref('account.rsa'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,

        })
        self.rule_dunning = self.rule_obj.create({
            'name': 'Dunning Fees',
            'rule_type': 'dunning_fees',
            'operations': [(6, 0, (self.operation_dunning.id, ))],
            'sequence': 1,
        })
        self.operation_round_1 = self.operation_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'label': 'Rounding',
            'account_id': self.ref('account.rsa'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,

        })
        self.rule_round_1 = self.rule_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'rule_type': 'rounding',
            'operations': [(6, 0, (self.operation_round_1.id, ))],
            'amount_min': -1.0,
            'amount_max': 0,
            'sequence': 2,
        })

    def test_paid_dunning_fees(self):
        """Customer paid the dunning fees of 10.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 10, [10]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_dunning)

    def test_no_paid_dunning_fees(self):
        """Customer paid the dunning fees of 10.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 0, [10]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_paid_part_of_dunning_fees(self):
        """Customer paid only 5.- of the dunning fees of 10.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 5, [10]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_dunning)

    def test_paid_too_much_dunning_fees(self):
        """Customer paid 15.- of the dunning fees of 10.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 15, [10]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_paid_no_dunning_fees_and_less_amount(self):
        """Customer paid 0.- of the dunning fees of 10.- and 1.- less"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, -1, [10]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_round_1)

    def test_paid_dunning_fees_several(self):
        """Customer paid 15.- of the dunning fees of 5.-, 10.- and 15.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 15, [5, 10, 15]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_dunning)

    def test_paid_too_much_dunning_fees_several(self):
        """Customer paid 16.- of the dunning fees of 5.-, 10.- and 15.-"""
        statement_line, move_line, __ = prepare_statement_with_dunning_fees(
            self, 16, [5, 10, 15]
        )
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_ignored_credit_control_line(self):
        """Customer paid 15.- of the fees of 5.-, 10.- and draft 15.-"""
        prepare = prepare_statement_with_dunning_fees
        statement_line, move_line, control_lines = prepare(
            self, 15, [5, 10, 15]
        )
        for control_line in control_lines:
            if control_line.dunning_fees_amount == 15:
                control_line.state = 'draft'
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_ignored_credit_control_line_take_other(self):
        """Customer paid 10.- of the fees of 5.-, 10.- and draft 15.-"""
        prepare = prepare_statement_with_dunning_fees
        statement_line, move_line, control_lines = prepare(
            self, 10, [5, 10, 15]
        )
        for control_line in control_lines:
            if control_line.dunning_fees_amount == 15:
                control_line.state = 'draft'
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_dunning)
