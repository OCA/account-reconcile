# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp import fields, exceptions


class TestReconcile(common.TransactionCase):

    def setUp(self):
        super(TestReconcile, self).setUp()
        self.rec_history_obj = self.registry('mass.reconcile.history')
        self.mass_rec_obj = self.registry('account.mass.reconcile')
        self.mass_rec_method_obj = (
            self.registry('account.mass.reconcile.method')
        )
        self.mass_rec = self.mass_rec_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'AER2',
                'account': self.ref('account.a_salary_expense'),
            }
            )
        self.mass_rec_method = self.mass_rec_method_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'mass.reconcile.simple.name',
                'sequence': '10',
                'task_id': self.mass_rec,
            }
            )
        self.mass_rec_no_history = self.mass_rec_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'AER3',
                'account': self.ref('account.a_salary_expense'),

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

    def test_last_history(self):
        mass_rec_last_hist = self.mass_rec_obj.browse(
            self.cr,
            self.uid,
            self.mass_rec
            ).last_history.id
        self.assertEqual(self.rec_history, mass_rec_last_hist)

    def test_last_history_empty(self):
        mass_rec_last_hist = self.mass_rec_obj.browse(
            self.cr,
            self.uid,
            self.mass_rec_no_history
            ).last_history.id
        self.assertEqual(False, mass_rec_last_hist)

    def test_last_history_full_no_history(self):
        with self.assertRaises(exceptions.Warning):
            self.mass_rec_obj.last_history_reconcile(
                self.cr, self.uid, [self.mass_rec_no_history])

    def test_open_unreconcile(self):
        res = self.mass_rec_obj.open_unreconcile(
            self.cr,
            self.uid,
            [self.mass_rec]
            )
        self.assertEqual(unicode([('id', 'in', [])]), res.get('domain', []))

    def test_prepare_run_transient(self):
        res = self.mass_rec_obj._prepare_run_transient(
            self.cr,
            self.uid,
            self.mass_rec_method_obj.browse(
                self.cr,
                self.uid,
                self.mass_rec_method
                )
            )
        self.assertEqual(self.ref('account.a_salary_expense'),
                         res.get('account_id', 0))


class TestReconcileNoMassReconcileAvailable(common.TransactionCase):

    def setUp(self):
        super(TestReconcileNoMassReconcileAvailable, self).setUp()
        self.rec_history_obj = self.registry('mass.reconcile.history')
        self.mass_rec_obj = self.registry('account.mass.reconcile')

#     def test_run_scheduler(self):
#         with self.assertRaises(AssertionError):
#             self.mass_rec_obj.run_scheduler(
#                 self.cr, self.uid)
