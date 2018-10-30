# -*- coding: utf-8 -*-
# © 2018 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountSetReconcilable(TransactionCase):

    def setUp(self):
        super(TestAccountSetReconcilable, self).setUp()
        account_account_model = self.env['account.account']
        account_move_model = self.env['account.move']
        journal = self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1)
        self.account1 = account_account_model.create({
            'name': 'account_test',
            'code': 'code_test',
            'reconcile': False,
            'user_type_id': self.env.ref(
                'account.data_account_type_current_liabilities').id,
        })
        self.move1 = account_move_model.create({
            'journal_id': journal.id,
            'ref': 'move_test',
            'line_ids': [(0, 0, {
                'name': 'foo',
                'debit': 10,
                'account_id': self.account1.id,
            }), (0, 0, {
                'name': 'bar',
                'credit': 10,
                'account_id': self.account1.id,
            })]
        })

    def test_write(self):
        self.account1.reconcile = True
        self.assertTrue(self.account1.reconcile)
        self.assertEqual(len(self.move1.line_ids), 2)
