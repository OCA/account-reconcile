from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.job import Job


class TestReconcileAsJob(TransactionCase):
    def test_reconcile_as_job(self):
        self.cr.execute("delete from queue_job")

        # set param to run reconcile as job
        self.env["ir.config_parameter"].sudo().set_param(
            "account.mass.reconcile.as.job", True
        )
        as_job = (
            self.env["ir.config_parameter"]
            .sudo()
            .set_param("account.mass.reconcile.as.job", True)
        )
        self.assertTrue(as_job)

        model = self.env["account.mass.reconcile"]
        job_1 = model.with_delay().reconcile_as_job()
        self.assertEqual(job_1.db_record().state, "pending")
        job = Job.load(self.env, job_1.uuid)
        job.perform()
        job.set_done()
        job.store()

        job_domain = [
            ("uuid", "=", job_1.uuid),
        ]
        job_1 = self.env["queue.job"].search(job_domain)
        self.assertEqual(job_1.state, "done")
