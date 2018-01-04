# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import fields, tools
from odoo.modules import get_module_resource


class TestReconcileHistory(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestReconcileHistory, cls).setUpClass()
        tools.convert_file(cls.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        cls.rec_history_obj = cls.env['mass.reconcile.history']
        cls.mass_rec_obj = cls.env['account.mass.reconcile']
        cls.mass_rec = cls.mass_rec_obj.create(
            {
                'name': 'AER1',
                'account': cls.env.ref('account.a_expense').id,

            }
            )
        cls.rec_history = cls.rec_history_obj.create(
            {
                'mass_reconcile_id': cls.mass_rec.id,
                'date': fields.Datetime.now(),
            }
            )

    def test_open_full_empty(self):
        res = self.rec_history._open_move_lines()
        self.assertEqual([('id', 'in', [])], res.get(
            'domain', []))

    def test_open_full_empty_from_method(self):
        res = self.rec_history.open_reconcile()
        self.assertEqual([('id', 'in', [])], res.get(
            'domain', []))
