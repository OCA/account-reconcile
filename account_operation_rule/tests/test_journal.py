# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestJournal(TransactionCase):

    def test_open_reconciliation_rules(self):
        # Just test that method returned the good view

        result = self.env['account.journal'].open_reconciliation_rules()
        self.assertEqual('account.operation.rule', result['res_model'])
        self.assertEqual('form', result['view_type'])
