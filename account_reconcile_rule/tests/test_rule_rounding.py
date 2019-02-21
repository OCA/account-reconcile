# Author: Guewen Baconnier
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import AccountReconciliationModelTestCase


class TestRuleRounding(AccountReconciliationModelTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reconcile_model_round_1 = cls.reconcile_model_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'label': 'Rounding',
            'amount_type': 'percentage',
            'amount': 100.0,

        })
        cls.rule_round_1 = cls.rule_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'rule_type': 'rounding',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_round_1.id, ))],
            'amount_min': -1.0,
            'amount_max': 0,
            'sequence': 1,
        })
        cls.reconcile_model_round_2 = cls.reconcile_model_obj.create({
            'name': 'Rounding -2.0 to -1.0',
            'label': 'Rounding',
            'amount_type': 'percentage',
            'amount': 100.0,

        })
        cls.rule_round_2 = cls.rule_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'rule_type': 'rounding',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_round_2.id, ))],
            'amount_min': -2.0,
            'amount_max': -1.0,
            'sequence': 2,
        })
        cls.reconcile_model_round_3 = cls.reconcile_model_obj.create({
            'name': 'Rounding 0.0 to 2.0',
            'label': 'Rounding',
            'amount_type': 'percentage',
            'amount': 100.0,

        })
        cls.rule_round_3 = cls.rule_obj.create({
            'name': 'Rounding 0.0 to 2.0',
            'rule_type': 'rounding',
            'reconcile_model_ids': [
                (6, 0, (cls.reconcile_model_round_3.id, ))],
            'amount_min': 0,
            'amount_max': 2,
            'sequence': 2,
        })

    def test_rule_round_1(self):
        """-0.5 => rule round 1"""
        statement_line, move_line = self.prepare_statement(-0.5)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_1)

    def test_rule_round_1_limit(self):
        """-1 => rule round 1"""
        statement_line, move_line = self.prepare_statement(-1)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_1)

    def test_rule_round_1_near_limit(self):
        """-1.0001 => rule round 1"""
        statement_line, move_line = self.prepare_statement(-1.0001)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_1)

    def test_rule_round_2(self):
        """-1.01 => rule round 2"""
        statement_line, move_line = self.prepare_statement(-1.01)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_2)

    def test_rule_round_2_limit(self):
        """-2 => rule round 2"""
        statement_line, move_line = self.prepare_statement(-2)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_2)

    def test_rule_round_3(self):
        """+1.5 => rule round 3"""
        statement_line, move_line = self.prepare_statement(1.5)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_3)

    def test_rule_round_3_limit(self):
        """+2 => rule round 3"""
        statement_line, move_line = self.prepare_statement(2)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertEqual(rule, self.rule_round_3)

    def test_rule_no_round_below(self):
        """-3 => no rule"""
        statement_line, move_line = self.prepare_statement(-3)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_rule_no_round_above(self):
        """+3 => no rule"""
        statement_line, move_line = self.prepare_statement(3)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_rule_no_round_zero(self):
        """0 => no rule"""
        statement_line, move_line = self.prepare_statement(0)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_rule_no_round_near_zero(self):
        """0.0001 => no rule"""
        statement_line, move_line = self.prepare_statement(0.0001)
        rule = self.rule_obj.find_first_rule(statement_line, [move_line])
        self.assertFalse(rule)

    def test_operations(self):
        """test models_for_reconciliation()"""
        statement_line, move_line = self.prepare_statement(-0.5)
        ops = self.rule_obj.models_for_reconciliation(statement_line.id,
                                                      move_line.ids)
        self.assertEqual(ops, self.reconcile_model_round_1)

    def test_multicurrency_lines(self):
        """No rounding rules on multi-currency lines"""
        currency = self.env.ref('base.AED')
        statement_line, move_line = self.prepare_statement(
            -0.5,
            statement_line_currency=currency,
            move_line_currency=currency
        )
        ops = self.rule_obj.models_for_reconciliation(statement_line.id,
                                                      move_line.ids)
        self.assertFalse(ops)
