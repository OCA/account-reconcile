# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import TransactionCase


class SomethingAccountReconcileModelInclusion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_two_blocks = cls.env.ref(
            "account_reconcile_model_inclusion.model_rule_two_blocks"
        )
        cls.rule_three_blocks = cls.env.ref(
            "account_reconcile_model_inclusion.model_rule_three_blocks"
        )
        cls.rule_three_blocks_xx = cls.env.ref(
            "account_reconcile_model_inclusion.model_rule_three_blocks_xx"
        )
        cls.rule_both = cls.env.ref("account_reconcile_model_inclusion.model_rule_both")
        cls.rule_both_xx = cls.env.ref(
            "account_reconcile_model_inclusion.model_rule_both_xx"
        )

    def test_account_reconcile_model_inclusion(self):
        """Test that inclusion/exclusion works"""
        StatementLine = self.env["account.bank.statement.line"]
        Partner = self.env["res.partner"]

        line = StatementLine.new({})

        def assertApplicable(rule):
            nonlocal line
            self.assertTrue(rule._is_applicable_for(line, Partner))

        def assertNotApplicable(rule):
            nonlocal line
            self.assertFalse(rule._is_applicable_for(line, Partner))

        line.payment_ref = "XX 42 42"
        assertApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks)
        assertNotApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both)

        line.payment_ref = "hello XX 42 42 world"
        assertApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks)
        assertNotApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both)

        line.payment_ref = "hello XY 42 42 42 world"
        assertNotApplicable(self.rule_two_blocks)
        assertApplicable(self.rule_three_blocks)
        assertNotApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both)

        line.payment_ref = "hello XY 42 42 42/XX 42 42 world"
        assertNotApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks)
        assertNotApplicable(self.rule_three_blocks_xx)
        assertApplicable(self.rule_both)

        line.payment_ref = "hello XX 42 42 42/XX 42 42 world"
        assertNotApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks)
        assertApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both)
        assertApplicable(self.rule_both_xx)

        line.payment_ref = "hello XX 42 42 42 world"
        assertNotApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks)
        assertApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both)

        self.rule_three_blocks_xx.exclude_reconcile_model_ids = self.rule_two_blocks
        self.rule_two_blocks.exclude_reconcile_model_ids = self.rule_three_blocks_xx
        line.payment_ref = "hello XX 42 42 42/XX 42 42 world"
        assertNotApplicable(self.rule_two_blocks)
        assertNotApplicable(self.rule_three_blocks_xx)
        assertNotApplicable(self.rule_both_xx)
