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

from .common import prepare_statement


class TestRuleCurrency(common.TransactionCase):

    def setUp(self):
        super(TestRuleCurrency, self).setUp()
        self.operation_obj = self.env['account.statement.operation.template']
        self.rule_obj = self.env['account.statement.operation.rule']
        self.aed = self.browse_ref('base.AED')
        self.afn = self.browse_ref('base.AFN')
        self.all = self.browse_ref('base.ALL')
        self.amd = self.browse_ref('base.AMD')
        self.aoa = self.browse_ref('base.AOA')
        self.operation_currency_1 = self.operation_obj.create({
            'name': 'Currency AED, AFR, ALL -1.0 to 0.0',
            'label': 'Currency',
            'account_id': self.ref('account.rsa'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,
        })
        self.rule_currency_1 = self.rule_obj.create({
            'name': 'Currency AED, AFR, ALL -1.0 to 0.0',
            'rule_type': 'currency',
            'operations': [(6, 0, (self.operation_currency_1.id, ))],
            'amount_min': -1.0,
            'amount_max': 0,
            'sequence': 1,
            'currencies': [(6, 0, [self.aed.id, self.afn.id, self.all.id])],
        })
        self.operation_currency_2 = self.operation_obj.create({
            'name': 'Currency AED, AFR, ALL -2.0 to -1.0',
            'label': 'Currency',
            'account_id': self.ref('account.rsa'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,
        })
        self.rule_currency_2 = self.rule_obj.create({
            'name': 'Currency AED, AFR, ALL -2.0 to 1.0',
            'rule_type': 'currency',
            'operations': [(6, 0, (self.operation_currency_2.id, ))],
            'amount_min': -2.0,
            'amount_max': -1.0,
            'sequence': 2,
            'currencies': [(6, 0, [self.aed.id, self.afn.id, self.all.id])],
        })
        self.operation_currency_3 = self.operation_obj.create({
            'name': 'Currency AMD, AOA -2.0 to 0.0',
            'label': 'Currency',
            'account_id': self.ref('account.rsa'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,

        })
        self.rule_currency_3 = self.rule_obj.create({
            'name': 'Currency AMD, AOA -2.0 to 0.0',
            'rule_type': 'currency',
            'operations': [(6, 0, (self.operation_currency_3.id, ))],
            'amount_min': -2,
            'amount_max': 0,
            'sequence': 2,
            'currencies': [(6, 0, [self.amd.id, self.aoa.id])],
        })

    def test_no_currency_match(self):
        """No rules for the current currency"""
        sek = self.browse_ref('base.SEK')
        statement_line, move_line = prepare_statement(
            self, -0.5,
            statement_line_currency=sek,
            move_line_currency=sek)
        ops = self.rule_obj.operations_for_reconciliation(statement_line.id,
                                                          move_line.ids)
        self.assertFalse(ops)

    def test_rounding_lines(self):
        """No Currencies rules on lines with company currency"""
        statement_line, move_line = prepare_statement(self, -0.5)
        ops = self.rule_obj.operations_for_reconciliation(statement_line.id,
                                                          move_line.ids)
        self.assertFalse(ops)

    def test_currency_rule_1(self):
        """Rule 1 is found with -0.5 AED"""
        statement_line, move_line = prepare_statement(
            self, -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_1)

    def test_currency_rule_2(self):
        """Rule 2 is found with -2 AED"""
        statement_line, move_line = prepare_statement(
            self, -2,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_2)

    def test_currency_rule_3(self):
        """Rule 3 is found with -2 AOA"""
        statement_line, move_line = prepare_statement(
            self, -2,
            statement_line_currency=self.aoa,
            move_line_currency=self.aoa,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_3)

    def test_currency_rule_not_in_bounds(self):
        """No rule is found with -3 AOA"""
        statement_line, move_line = prepare_statement(
            self, -3,
            statement_line_currency=self.aoa,
            move_line_currency=self.aoa,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_no_rule_amount_currency_different(self):
        """No rule when amount currency is different"""
        statement_line, move_line = prepare_statement(
            self, -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0.5)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_rule_amount_currency_difference_near_zero(self):
        """Apply the rule when the difference is near 0"""
        statement_line, move_line = prepare_statement(
            self, -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=-0.001)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_1)
