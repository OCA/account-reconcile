# -*- coding: utf-8 -*-
# Author: Guewen Baconnier
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import AccountOperationTestCase


class TestRuleCurrency(AccountOperationTestCase):

    def setUp(self):
        super(TestRuleCurrency, self).setUp()
        self.operation_obj = self.env['account.operation.template']
        self.rule_obj = self.env['account.operation.rule']
        self.aed = self.browse_ref('base.AED')
        self.aed.active = True
        self.afn = self.browse_ref('base.AFN')
        self.afn.active = True
        self.all = self.browse_ref('base.ALL')
        self.all.active = True
        self.amd = self.browse_ref('base.AMD')
        self.amd.active = True
        self.aoa = self.browse_ref('base.AOA')
        self.aoa.active = True

        self.operation_currency_1 = self.operation_obj.create({
            'name': 'Currency AED, AFR, ALL -1.0 to 0.0',
            'label': 'Currency',
            'account_id': self.account_receivable.id,
            'amount_type': 'percentage',
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
            'amount_type': 'percentage',
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
            'amount_type': 'percentage',
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
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=sek,
            move_line_currency=sek)
        ops = self.rule_obj.operations_for_reconciliation(statement_line.id,
                                                          move_line.ids)
        self.assertFalse(ops)

    def test_rounding_lines(self):
        """No Currencies rules on lines with company currency"""
        statement_line, move_line = self.prepare_statement(-0.5)
        ops = self.rule_obj.operations_for_reconciliation(statement_line.id,
                                                          move_line.ids)
        self.assertFalse(ops)

    def test_currency_rule_1(self):
        """Rule 1 is found with -0.5 AED"""
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_1)

    def test_currency_rule_2(self):
        """Rule 2 is found with -2 AED"""
        statement_line, move_line = self.prepare_statement(
            -2,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_2)

    def test_currency_rule_3(self):
        """Rule 3 is found with -2 AOA"""
        statement_line, move_line = self.prepare_statement(
            -2,
            statement_line_currency=self.aoa,
            move_line_currency=self.aoa,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_3)

    def test_currency_rule_not_in_bounds(self):
        """No rule is found with -3 AOA"""
        statement_line, move_line = self.prepare_statement(
            -3,
            statement_line_currency=self.aoa,
            move_line_currency=self.aoa,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_no_rule_amount_currency_different(self):
        """No rule when amount currency is different"""
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0.5)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_rule_amount_currency_difference_near_zero(self):
        """Apply the rule when the difference is near 0"""
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=-0.001)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEquals(rule, self.rule_currency_1)
