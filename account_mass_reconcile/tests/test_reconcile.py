# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests
from odoo import exceptions, fields

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestReconcile(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super(TestReconcile, cls).setUpClass()
        cls.rec_history_obj = cls.env["mass.reconcile.history"]
        cls.mass_rec_obj = cls.env["account.mass.reconcile"]
        cls.mass_rec_method_obj = cls.env["account.mass.reconcile.method"]

        cls.sale_journal = cls.company_data["default_journal_sale"]
        cls.mass_rec = cls.mass_rec_obj.create(
            {"name": "Sale Account", "account": cls.sale_journal.default_account_id.id}
        )
        cls.mass_rec_method = cls.mass_rec_method_obj.create(
            {
                "name": "mass.reconcile.simple.name",
                "sequence": "10",
                "task_id": cls.mass_rec.id,
            }
        )
        cls.mass_rec_no_history = cls.mass_rec_obj.create(
            {"name": "AER3", "account": cls.sale_journal.default_account_id.id}
        )
        cls.rec_history = cls.rec_history_obj.create(
            {"mass_reconcile_id": cls.mass_rec.id, "date": fields.Datetime.now()}
        )

    def test_last_history(self):
        mass_rec_last_hist = self.mass_rec.last_history
        self.assertEqual(self.rec_history, mass_rec_last_hist)

    def test_last_history_empty(self):
        mass_rec_last_hist = self.mass_rec_no_history.last_history.id
        self.assertEqual(False, mass_rec_last_hist)

    def test_last_history_full_no_history(self):
        with self.assertRaises(exceptions.UserError):
            self.mass_rec_no_history.last_history_reconcile()

    def test_open_unreconcile(self):
        res = self.mass_rec.open_unreconcile()
        self.assertEqual([("id", "in", [])], res.get("domain", []))

    def test_prepare_run_transient(self):
        res = self.mass_rec._prepare_run_transient(self.mass_rec_method)
        self.assertEqual(
            self.sale_journal.default_account_id.id, res.get("account_id", 0)
        )

    def test_open_full_empty(self):
        res = self.rec_history._open_move_lines()
        self.assertEqual([("id", "in", [])], res.get("domain", []))

    def test_open_full_empty_from_method(self):
        res = self.rec_history.open_reconcile()
        self.assertEqual([("id", "in", [])], res.get("domain", []))
