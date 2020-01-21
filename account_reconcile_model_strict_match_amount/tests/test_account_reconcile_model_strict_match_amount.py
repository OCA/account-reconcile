# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.account.tests.test_reconciliation_matching_rules import TestReconciliationMatchingRules


class TestAccountReconcileModelStrictMatchAmount(TestReconciliationMatchingRules):

    def setUp(self):
        super().setUp()
        self.partner_3 = self.env['res.partner'].create({'name': 'partner_3'})
        self.partner_4 = self.env['res.partner'].create({'name': 'partner_4'})
        self.invoice_line_5 = self._create_invoice_line(
            150, self.partner_3, 'out_invoice'
        )
        self.invoice_line_5.ref = 'ABC001XYZ'
        self.invoice_line_6 = self._create_invoice_line(
            300, self.partner_4, 'out_invoice'
        )
        self.invoice_line_6.name = 'ABC002XYZ'

        self.bank_st_2 = self.env['account.bank.statement'].create({
            'name': 'test bank journal 2', 'journal_id': self.bank_journal.id,
        })

        self.bank_line_3 = self.env['account.bank.statement.line'].create({
            'statement_id': self.bank_st_2.id,
            'name': 'ABC001XYZ',
            'partner_id': self.partner_3.id,
            'amount': 70,
            'sequence': 1,
        })
        self.bank_line_4 = self.env['account.bank.statement.line'].create({
            'statement_id': self.bank_st_2.id,
            'name': 'ABC002XYZ',
            'partner_id': self.partner_4.id,
            'amount': 270,
            'sequence': 1,
        })

    def test_auto_reconcile_strict_match_100(self):
        my_rule = self.env['account.reconcile.model'].create({
            'name': 'Strict Invoice matching amount 100%',
            'rule_type': 'invoice_matching',
            'auto_reconcile': True,
            'match_nature': 'both',
            'match_partner': True,
            'match_same_currency': True,
            'match_total_amount': True,
            'match_total_amount_param': 100.0,
            'strict_match_total_amount': True,
            # 'match_partner_ids': [
            #     (6, 0, [self.partner_3.id, self.partner_4.id])
            # ],
        })

        self._check_statement_matching(my_rule, {
            self.bank_line_3.id: {'aml_ids': []},
            self.bank_line_4.id: {'aml_ids': []},
        }, statements=self.bank_st_2)

    def test_auto_reconcile_strict_match_80(self):
        my_rule = self.env['account.reconcile.model'].create({
            'name': 'Strict Invoice matching amount 80%',
            'rule_type': 'invoice_matching',
            'auto_reconcile': True,
            'match_nature': 'both',
            'match_partner': True,
            'match_same_currency': True,
            'match_total_amount': True,
            'match_total_amount_param': 80.0,
            'strict_match_total_amount': True,
            # 'match_partner_ids': [
            #     (6, 0, [self.partner_3.id, self.partner_4.id])
            # ],
        })

        self._check_statement_matching(my_rule, {
            self.bank_line_3.id: {'aml_ids': []},
            self.bank_line_4.id: {'aml_ids': [self.invoice_line_6.id], 'model': my_rule, 'status': 'reconciled'},
        }, statements=self.bank_st_2)
