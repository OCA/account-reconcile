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
from openerp import fields


class testReconcileHistory(common.TransactionCase):

    def setUp(self):
        super(testReconcileHistory, self).setUp()
        self.rec_history_obj = self.registry('easy.reconcile.history')
        self.easy_rec_obj = self.registry('account.easy.reconcile')
        self.easy_rec = self.easy_rec_obj.create(
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
                'easy_reconcile_id': self.easy_rec,
                'date': fields.Datetime.now(),
            }
            )

    def test_assert_open_full_partial(self):
        word = 'test'
        with self.assertRaises(AssertionError):
            self.rec_history_obj._open_move_lines(
                self.cr, self.uid, [self.rec_history], word)

    def test_open_full_empty(self):
        res = self.rec_history_obj._open_move_lines(
            self.cr, self.uid, [self.rec_history], 'full')
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))

    def test_open_full_empty_from_method(self):
        res = self.rec_history_obj.open_reconcile(
            self.cr, self.uid, [self.rec_history])
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))

    def test_open_partial_empty(self):
        res = self.rec_history_obj._open_move_lines(
            self.cr, self.uid, [self.rec_history], 'partial')
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))

    def test_open_partial_empty_from_method(self):
        res = self.rec_history_obj.open_partial(
            self.cr, self.uid, [self.rec_history])
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))
