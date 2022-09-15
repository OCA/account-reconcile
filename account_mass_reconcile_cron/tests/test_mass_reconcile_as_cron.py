# © 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestMassReconcileAsCron(TestAccountReconciliationCommon):
    def test_reconcile_as_cron(self):
        invoice = self.create_invoice()
        self.assertEqual("posted", invoice.state)

        receivalble_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.company_data["default_journal_bank"].id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        self.env["account.mass.reconcile"].create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
                "is_cron_executed": True,
            }
        )
        # call the automatic reconcilation method
        mass_reconcile_cron = self.env["ir.cron"].search(
            [("name", "=", "Start Auto Reconciliation")]
        )
        mass_reconcile_cron.method_direct_trigger()
        self.assertEqual("paid", invoice.payment_state)
