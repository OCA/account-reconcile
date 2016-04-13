# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp import fields


class TestReconcileHistory(common.TransactionCase):

    def setUp(self):
        super(TestReconcileHistory, self).setUp()
        self.rec_history_obj = self.registry('mass.reconcile.history')
        self.mass_rec_obj = self.registry('account.mass.reconcile')
        self.mass_rec = self.mass_rec_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'AER1',
                'account': self.ref('account.a_expense'),

            }
            )
        self.rec_history = self.rec_history_obj.create(
            self.cr,
            self.uid,
            {
                'mass_reconcile_id': self.mass_rec,
                'date': fields.Datetime.now(),
            }
            )

    def test_open_full_empty(self):
        res = self.rec_history_obj._open_move_lines(
            self.cr, self.uid, [self.rec_history])
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))

    def test_open_full_empty_from_method(self):
        res = self.rec_history_obj.open_reconcile(
            self.cr, self.uid, [self.rec_history])
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))
