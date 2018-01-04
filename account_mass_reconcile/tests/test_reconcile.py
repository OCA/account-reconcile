# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import fields, exceptions, tools
from odoo.modules import get_module_resource


class TestReconcile(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestReconcile, cls).setUpClass()
        tools.convert_file(cls.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        cls.rec_history_obj = cls.env['mass.reconcile.history']
        cls.mass_rec_obj = cls.env['account.mass.reconcile']
        cls.mass_rec_method_obj = (
            cls.env['account.mass.reconcile.method']
        )
        cls.mass_rec = cls.mass_rec_obj.create({
            'name': 'AER2',
            'account': cls.env.ref('account.a_salary_expense').id,
        })
        cls.mass_rec_method = cls.mass_rec_method_obj.create({
            'name': 'mass.reconcile.simple.name',
            'sequence': '10',
            'task_id': cls.mass_rec.id,
        })
        cls.mass_rec_no_history = cls.mass_rec_obj.create({
            'name': 'AER3',
            'account': cls.env.ref('account.a_salary_expense').id,
        })
        cls.rec_history = cls.rec_history_obj.create({
            'mass_reconcile_id': cls.mass_rec.id,
            'date': fields.Datetime.now(),
        })

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
        self.assertEqual([('id', 'in', [])], res.get('domain', []))

    def test_prepare_run_transient(self):
        res = self.mass_rec._prepare_run_transient(self.mass_rec_method)
        self.assertEqual(self.ref('account.a_salary_expense'),
                         res.get('account_id', 0))
