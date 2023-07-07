# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestReconciliation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_partner_mismatch=True
            )
        )
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner_id = cls.partner.id
        cls.account_rcv = cls.env["account.account"].create(
            {
                "code": "RA1000",
                "name": "Test Receivable Account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.account_rsa = cls.env["account.account"].create(
            {
                "code": "PA1000",
                "name": "Test Payable Account",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        cls.aml = cls.init_moves()

    @classmethod
    def create_move(cls, name, amount):
        debit_line_vals = {
            "name": name,
            "debit": amount > 0 and amount or 0.0,
            "credit": amount < 0 and -amount or 0.0,
            "account_id": cls.account_rcv.id,
        }
        credit_line_vals = debit_line_vals.copy()
        credit_line_vals["debit"] = debit_line_vals["credit"]
        credit_line_vals["credit"] = debit_line_vals["debit"]
        credit_line_vals["account_id"] = cls.account_rsa.id
        vals = {
            "journal_id": cls.bank_journal.id,
            "line_ids": [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
        }
        return (
            cls.env["account.move"]
            .with_context(default_journal_id=cls.bank_journal.id)
            .create(vals)
            .id
        )

    @classmethod
    def init_moves(cls):
        move_list_vals = [
            ("1", -1.83),
            ("2", 728.35),
            ("3", -4.46),
            ("4", 0.32),
            ("5", 14.72),
            ("6", -737.10),
        ]
        move_ids = []
        for name, amount in move_list_vals:
            move_ids.append(cls.create_move(name, amount))
        aml_recs = cls.env["account.move.line"].search(
            [("move_id", "in", move_ids), ("account_id", "=", cls.account_rcv.id)]
        )
        return aml_recs

    def test_reconcile_no_partner(self):
        self.aml.move_id.action_post()
        self.aml.reconcile()
        self.assertTrue(all(self.aml.mapped("reconciled")))

    def test_reconcile_partner_mismatch(self):
        self.aml[0].partner_id = self.partner.id
        with self.assertRaises(UserError):
            self.aml.reconcile()
        # all lines with same partner allowed
        self.aml.write({"partner_id": self.partner.id})
        self.aml.move_id.action_post()
        self.aml.reconcile()
        self.assertTrue(all(self.aml.mapped("reconciled")))

    def test_reconcile_accounts_excluded(self):
        self.aml[0].partner_id = self.partner.id
        with self.assertRaises(UserError):
            self.aml.reconcile()
        # reconciliation forbiden only for certain types of accounts
        account = self.env["account.account"].create(
            {
                "code": "CAA1000",
                "name": "Test Current Assets Account",
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
                "reconcile": True,
            }
        )
        self.aml[0].account_id = account.id
        with self.assertRaises(UserError):
            self.aml.reconcile()
        # reconciliation for different partners allowed
        # for not forbidden types
        self.aml.write({"account_id": account.id})
        self.aml.move_id.action_post()
        self.aml.reconcile()
        self.assertTrue(all(self.aml.mapped("reconciled")))
