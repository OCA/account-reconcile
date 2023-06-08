# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import tagged

from odoo.addons.account_mass_reconcile.tests.test_scenario_reconcile import (
    TestScenarioReconcile,
)
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("post_install", "-at_install")
class TestScenarioReconcileAsJob(TestScenarioReconcile):
    def test_scenario_reconcile_as_job(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "account.mass.reconcile.as.job", True
        )
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
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        with trap_jobs() as trap:
            # call the automatic reconcilation method
            mass_rec.run_reconcile()
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                mass_rec.reconcile_as_job,
                args=(),
            )
            job = trap.enqueued_jobs[0]
            self.assertEqual(job.state, "pending")
            trap.perform_enqueued_jobs()
            self.assertEqual("paid", invoice.payment_state)

    def test_scenario_reconcile_lines_as_job(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "account.mass.reconcile.as.job", True
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "account.mass.reconcile.lines.as.job", True
        )
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
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        with trap_jobs() as trap:
            self.assertFalse(self.env["mass.reconcile.simple.partner"].search([]))
            # call the automatic reconcilation method
            mass_rec.run_reconcile()
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                mass_rec.reconcile_as_job,
                args=(),
            )
            job = trap.enqueued_jobs[0]
            self.assertEqual(job.state, "pending")
            self.assertFalse(self.env["mass.reconcile.simple.partner"].search([]))
            trap.perform_enqueued_jobs()
            trap.assert_jobs_count(2)
            job_2 = trap.enqueued_jobs[1]
            # Cannot use assert_enqueue_job with all the parameters
            self.assertEqual(job_2.model_name, "mass.reconcile.simple.partner")
            self.assertEqual(job_2.method_name, "reconcile_lines_as_job")
            self.assertEqual(job_2.state, "pending")
            # Delete existing wizard to make sure the job can still after after
            #  the wizard is garbage collected
            wiz = self.env["mass.reconcile.simple.partner"].search([])
            self.assertTrue(wiz)
            wiz.unlink()
            trap.perform_enqueued_jobs()
            self.assertEqual("paid", invoice.payment_state)
