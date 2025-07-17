# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountPartnerReconcile(TransactionCase):
    """Tests for Account Partner Reconcile."""

    def setUp(self):
        super().setUp()

        self.partner1 = self.env.ref("base.res_partner_1")

    def test_account_partner_reconcile(self):
        receivable_account = self.partner1.property_account_receivable_id
        payable_account = self.partner1.property_account_payable_id

        # reconcile_mode="customers" (Match Receivables)
        res = self.partner1.with_context(
            reconcile_mode="customers"
        ).action_open_reconcile()
        expect = {
            "type": "ir.actions.act_window",
            "xml_id": "account_reconcile_oca.account_account_reconcile_act_window",
            "domain": [
                ("account_id", "=", receivable_account.id),
                ("partner_id", "=", self.partner1.id),
            ],
        }
        self.assertDictEqual(
            expect,
            {k: v for k, v in res.items() if k in expect},
            "There was an error and the Reconcile action couldn't be opened.",
        )

        # reconcile_mode="suppliers" (Match Payables)
        res = self.partner1.with_context(
            reconcile_mode="suppliers"
        ).action_open_reconcile()
        expect = {
            "type": "ir.actions.act_window",
            "xml_id": "account_reconcile_oca.account_account_reconcile_act_window",
            "domain": [
                ("account_id", "=", payable_account.id),
                ("partner_id", "=", self.partner1.id),
            ],
        }
        self.assertDictEqual(
            expect,
            {k: v for k, v in res.items() if k in expect},
            "There was an error and the Reconcile action couldn't be opened.",
        )
