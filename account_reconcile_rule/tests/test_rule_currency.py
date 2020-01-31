# Author: Guewen Baconnier
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import AccountReconciliationModelTestCase


class TestRuleCurrency(AccountReconciliationModelTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.aed = cls.env.ref('base.AED')
        cls.aed.active = True
        cls.afn = cls.env.ref('base.AFN')
        cls.afn.active = True
        cls.all = cls.env.ref('base.ALL')
        cls.all.active = True
        cls.amd = cls.env.ref('base.AMD')
        cls.amd.active = True
        cls.aoa = cls.env.ref('base.AOA')
        cls.aoa.active = True

        cls.reconcile_model_currency_1 = cls.reconcile_model_obj.create({
            'name': 'Currency AED, AFR, ALL -1.0 to 0.0',
            'label': 'Currency',
            'account_id': cls.account_receivable.id,
            'amount_type': 'percentage',
            'amount': 100.0,
        })
        cls.rule_currency_1 = cls.rule_obj.create({
            'name': 'Currency AED, AFR, ALL -1.0 to 0.0',
            'rule_type': 'currency',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_currency_1.id,))],
            'amount_min': -1.0,
            'amount_max': 0,
            'sequence': 1,
            'currency_ids': [(6, 0, [cls.aed.id, cls.afn.id, cls.all.id])],
        })

        cls.reconcile_model_currency_2 = cls.reconcile_model_obj.create({
            'name': 'Currency AED, AFR, ALL -2.0 to -1.0',
            'label': 'Currency',
            'amount_type': 'percentage',
            'amount': 100.0,
        })
        cls.rule_currency_2 = cls.rule_obj.create({
            'name': 'Currency AED, AFR, ALL -2.0 to 1.0',
            'rule_type': 'currency',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_currency_2.id, ))],
            'amount_min': -2.0,
            'amount_max': -1.0,
            'sequence': 2,
            'currency_ids': [(6, 0, [cls.aed.id, cls.afn.id, cls.all.id])],
        })

        cls.reconcile_model_currency_3 = cls.reconcile_model_obj.create({
            'name': 'Currency AMD, AOA -2.0 to 0.0',
            'label': 'Currency',
            'amount_type': 'percentage',
            'amount': 100.0,

        })
        cls.rule_currency_3 = cls.rule_obj.create({
            'name': 'Currency AMD, AOA -2.0 to 0.0',
            'rule_type': 'currency',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_currency_3.id, ))],
            'amount_min': -2,
            'amount_max': 0,
            'sequence': 2,
            'currency_ids': [(6, 0, [cls.amd.id, cls.aoa.id])],
        })

    def test_no_currency_match(self):
        """No rules for the current currency"""
        sek = self.browse_ref('base.SEK')
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=sek,
            move_line_currency=sek)
        ops = self.rule_obj.models_for_reconciliation(statement_line.id,
                                                      move_line.ids)
        self.assertFalse(ops)

    def test_rounding_lines(self):
        """No Currencies rules on lines with company currency"""
        statement_line, move_line = self.prepare_statement(-0.5)
        ops = self.rule_obj.models_for_reconciliation(statement_line.id,
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
        self.assertEqual(rule, self.rule_currency_1)

    def test_currency_rule_2(self):
        """Rule 2 is found with -2 AED"""
        statement_line, move_line = self.prepare_statement(
            -2,
            statement_line_currency=self.aed,
            move_line_currency=self.aed,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_currency_2)

    def test_currency_rule_3(self):
        """Rule 3 is found with -2 AOA"""
        statement_line, move_line = self.prepare_statement(
            -2,
            statement_line_currency=self.aoa,
            move_line_currency=self.aoa,
            amount_currency_difference=0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_currency_3)

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
        self.assertEqual(rule, self.rule_currency_1)
