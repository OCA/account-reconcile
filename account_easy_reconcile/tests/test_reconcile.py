# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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
from openerp import fields, exceptions


class testReconcile(common.TransactionCase):

    def setUp(self):
        super(testReconcile, self).setUp()
        self.rec_history_obj = self.registry('easy.reconcile.history')
        self.easy_rec_obj = self.registry('account.easy.reconcile')
        self.easy_rec_method_obj = (
            self.registry('account.easy.reconcile.method')
        )
        self.easy_rec = self.easy_rec_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'AER2',
                'account': self.ref('account.a_salary_expense'),
            }
            )
        self.easy_rec_method = self.easy_rec_method_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'easy.reconcile.simple.name',
                'sequence': '10',
                'task_id': self.easy_rec,
            }
            )
        self.easy_rec_no_history = self.easy_rec_obj.create(
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
                'easy_reconcile_id': self.easy_rec,
                'date': fields.Datetime.now(),
            }
            )

    def test_last_history(self):
        easy_rec_last_hist = self.easy_rec_obj.browse(
            self.cr,
            self.uid,
            self.easy_rec
            ).last_history.id
        self.assertEqual(self.rec_history, easy_rec_last_hist)

    def test_last_history_empty(self):
        easy_rec_last_hist = self.easy_rec_obj.browse(
            self.cr,
            self.uid,
            self.easy_rec_no_history
            ).last_history.id
        self.assertEqual(False, easy_rec_last_hist)

    def test_last_history_full_no_history(self):
        with self.assertRaises(exceptions.Warning):
            self.easy_rec_obj.last_history_reconcile(
                self.cr, self.uid, [self.easy_rec_no_history])

    def test_last_history_partial_no_history(self):
        with self.assertRaises(exceptions.Warning):
            self.easy_rec_obj.last_history_partial(
                self.cr, self.uid, [self.easy_rec_no_history])

    def test_open_unreconcile(self):
        res = self.easy_rec_obj.open_unreconcile(
            self.cr,
            self.uid,
            [self.easy_rec]
            )
        self.assertEqual(unicode([('id', 'in', [])]), res.get('domain', []))

    def test_open_partial_reconcile(self):
        res = self.easy_rec_obj.open_partial_reconcile(
            self.cr,
            self.uid,
            [self.easy_rec]
            )
        self.assertEqual(unicode([('id', 'in', [])]), res.get('domain', []))

    def test_prepare_run_transient(self):
        res = self.easy_rec_obj._prepare_run_transient(
            self.cr,
            self.uid,
            self.easy_rec_method_obj.browse(
                self.cr,
                self.uid,
                self.easy_rec_method
                )
            )
        self.assertEqual(self.ref('account.a_salary_expense'),
                         res.get('account_id', 0))


class testReconcileNoEasyReconcileAvailable(common.TransactionCase):

    def setUp(self):
        super(testReconcileNoEasyReconcileAvailable, self).setUp()
        self.rec_history_obj = self.registry('easy.reconcile.history')
        self.easy_rec_obj = self.registry('account.easy.reconcile')

#     def test_run_scheduler(self):
#         with self.assertRaises(AssertionError):
#             self.easy_rec_obj.run_scheduler(
#                 self.cr, self.uid)
