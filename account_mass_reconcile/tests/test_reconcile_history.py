# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import fields, tools
from odoo.modules import get_module_resource


class TestReconcileHistory(common.TransactionCase):

    def setUp(self):
        super(TestReconcileHistory, self).setUp()
        tools.convert_file(self.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        self.rec_history_obj = self.env['mass.reconcile.history']
        self.mass_rec_obj = self.env['account.mass.reconcile']
        self.mass_rec = self.mass_rec_obj.create(
            {
                'name': 'AER1',
                'account': self.ref('account.a_expense'),

            }
            )
        self.rec_history = self.rec_history_obj.create(
            {
                'mass_reconcile_id': self.mass_rec.id,
                'date': fields.Datetime.now(),
            }
            )

    def test_open_full_empty(self):
        res = self.rec_history._open_move_lines()
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))

    def test_open_full_empty_from_method(self):
        res = self.rec_history.open_reconcile()
        self.assertEqual(unicode([('id', 'in', [])]), res.get(
            'domain', []))
