# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import fields, exceptions, tools
from odoo.modules import get_module_resource


class TestReconcile(common.TransactionCase):

    def setUp(self):
        super(TestReconcile, self).setUp()
        tools.convert_file(self.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        self.rec_history_obj = self.env['mass.reconcile.history']
        self.mass_rec_obj = self.env['account.mass.reconcile']
        self.mass_rec_method_obj = (
            self.env['account.mass.reconcile.method']
        )
        self.mass_rec = self.mass_rec_obj.create(
            {
                'name': 'AER2',
                'account': self.ref('account.a_salary_expense'),
            }
            )
        self.mass_rec_method = self.mass_rec_method_obj.create(
            {
                'name': 'mass.reconcile.simple.name',
                'sequence': '10',
                'task_id': self.mass_rec.id,
            }
            )
        self.mass_rec_no_history = self.mass_rec_obj.create(
            {
                'name': 'AER3',
                'account': self.ref('account.a_salary_expense'),

            }
            )
        self.rec_history = self.rec_history_obj.create(
            {
                'mass_reconcile_id': self.mass_rec.id,
                'date': fields.Datetime.now(),
            }
            )

    def test_last_history(self):
        mass_rec_last_hist = self.mass_rec.last_history
        self.assertEqual(self.rec_history, mass_rec_last_hist)

    def test_last_history_empty(self):
        mass_rec_last_hist = self.mass_rec_no_history.last_history.id
        self.assertEqual(False, mass_rec_last_hist)

    def test_last_history_full_no_history(self):
        with self.assertRaises(exceptions.Warning):
            self.mass_rec_no_history.last_history_reconcile()

    def test_open_unreconcile(self):
        res = self.mass_rec.open_unreconcile()
        self.assertEqual(unicode([('id', 'in', [])]), res.get('domain', []))

    def test_prepare_run_transient(self):
        res = self.mass_rec._prepare_run_transient(self.mass_rec_method)
        self.assertEqual(self.ref('account.a_salary_expense'),
                         res.get('account_id', 0))
