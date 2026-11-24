# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import Form, new_test_user, tagged

from .common import StripeImportCommon, balance_transaction


@tagged("post_install", "-at_install")
class TestStripeImport(StripeImportCommon):
    def test_cron_creates_one_stripe_entry_per_payout(self):
        self._add_simple_stripe_payout("po_1", 1700000000)
        self._add_simple_stripe_payout("po_2", 1700100000)

        self._run_stripe_import_cron()

        entries = self._stripe_entries()
        self.assertEqual(entries.mapped("ref"), ["po_1", "po_2"])
        for entry in entries:
            self.assertEqual(sum(entry.line_ids.mapped("debit")), 10.0)
            self.assertEqual(sum(entry.line_ids.mapped("credit")), 10.0)

    def test_stripe_entry_lines(self):
        self._add_stripe_payout(
            "po_1",
            1700100000,
            [
                balance_transaction(
                    "txn_1",
                    1000,
                    "charge",
                    "ch_1",
                    1700000000,
                    description="Order S00012",
                    fees=[("Stripe processing fees", 30)],
                ),
                balance_transaction(
                    "txn_2",
                    2000,
                    "charge",
                    "ch_2",
                    1700000000,
                    description="Order S00013",
                    fees=[
                        ("Stripe processing fees", 60),
                        ("Stripe currency conversion fee", 10),
                    ],
                ),
                balance_transaction(
                    "txn_3",
                    -500,
                    "refund",
                    "re_1",
                    1700050000,
                    description="REFUND FOR CHARGE (Order S00012)",
                ),
                balance_transaction(
                    "txn_4",
                    -2400,
                    "payout",
                    "po_1",
                    1700100000,
                    description="STRIPE PAYOUT",
                ),
            ],
        )

        self._run_stripe_import_cron()

        receivable = self.company_data["default_account_receivable"]
        commission = self.company_data["default_account_expense"]
        bank = self.stripe_journal.default_account_id
        self.assertCountEqual(
            [
                (line.name, line.account_id, line.partner_id, line.debit, line.credit)
                for line in self._stripe_entries().line_ids
            ],
            [
                ("Order S00012", receivable, self.env["res.partner"], 0.0, 10.0),
                ("Order S00013", receivable, self.env["res.partner"], 0.0, 20.0),
                (
                    "REFUND FOR CHARGE (Order S00012)",
                    receivable,
                    self.env["res.partner"],
                    5.0,
                    0.0,
                ),
                ("Stripe processing fees", commission, self.stripe_partner, 0.9, 0.0),
                (
                    "Stripe currency conversion fee",
                    commission,
                    self.stripe_partner,
                    0.1,
                    0.0,
                ),
                ("STRIPE PAYOUT", bank, self.stripe_partner, 24.0, 0.0),
            ],
        )

    def test_import_resumes_after_last_imported_payout(self):
        self._add_simple_stripe_payout("po_1", 1700000000)
        self._add_simple_stripe_payout("po_2", 1700100000)

        self._run_stripe_import_cron()

        self.assertEqual(
            self.stripe_journal.last_import_date, datetime(2023, 11, 16, 2, 0)
        )
        self._add_simple_stripe_payout("po_3", 1700200000)

        self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_1", "po_2", "po_3"])
        self.assertEqual(
            self.stripe_journal.last_import_date, datetime(2023, 11, 17, 5, 46, 40)
        )

    def test_import_all_payouts_beyond_one_page(self):
        for index in range(101):
            self._add_simple_stripe_payout(f"po_{index:03d}", 1700000000 + index)

        self._run_stripe_import_cron()

        self.assertEqual(len(self._stripe_entries()), 101)

    def test_import_all_transactions_beyond_one_page(self):
        charges = [
            balance_transaction(
                f"txn_{index}", 100, "charge", f"ch_{index}", 1700000000
            )
            for index in range(150)
        ]
        self._add_stripe_payout(
            "po_1",
            1700100000,
            charges
            + [balance_transaction("txn_po_1", -15000, "payout", "po_1", 1700100000)],
        )

        self._run_stripe_import_cron()

        entry = self._stripe_entries()
        self.assertEqual(len(entry.line_ids), 151)
        self.assertEqual(sum(entry.line_ids.mapped("credit")), 150.0)

    def test_rerun_does_not_import_a_payout_twice(self):
        self._add_simple_stripe_payout("po_1", 1700000000)
        self._run_stripe_import_cron()
        self.stripe_journal.last_import_date = False

        self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_1"])

    def test_import_uses_the_stripe_provider_of_the_journal_company(self):
        other_company_data = self.setup_other_company()
        other_provider = self._prepare_provider(
            "stripe",
            company=other_company_data["company"],
            update_values={"stripe_secret_key": "sk_test_other_company"},
        )
        other_journal = self._create_stripe_journal(other_company_data)
        self._add_simple_stripe_payout("po_company", 1700000000)
        self._add_simple_stripe_payout(
            "po_other_company", 1700000000, provider=other_provider
        )

        self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_company"])
        self.assertEqual(
            self._stripe_entries(other_journal).mapped("ref"), ["po_other_company"]
        )

    def test_wizard_imports_without_file(self):
        accountant = new_test_user(
            self.env,
            login="stripe_accountant",
            groups="account.group_account_manager,account.group_account_user",
            company_id=self.company_data["company"].id,
        )
        self._add_simple_stripe_payout("po_1", 1700000000)

        with Form(self.env["credit.statement.import"].with_user(accountant)) as form:
            form.journal_id = self.stripe_journal
        action = form.record.import_statement()

        self.assertEqual(self.env["account.move"].browse(action["res_id"]).ref, "po_1")

    def test_payout_paid_after_a_later_payout_is_imported(self):
        self._add_simple_stripe_payout("po_transit", 1700000000, status="in_transit")
        self._add_simple_stripe_payout("po_paid", 1700100000)

        self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_paid"])
        self.assertEqual(
            self.stripe_journal.last_import_date, datetime(2023, 11, 14, 22, 13, 20)
        )
        self._set_stripe_payout_status("po_transit", "paid")

        self._run_stripe_import_cron()

        self.assertEqual(
            self._stripe_entries().mapped("ref"), ["po_paid", "po_transit"]
        )

    def test_payout_arriving_the_same_day_as_an_imported_one_is_imported(self):
        self._add_simple_stripe_payout("po_1", 1700006400)
        self._run_stripe_import_cron()
        self._add_simple_stripe_payout("po_2", 1700006400)

        self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_1", "po_2"])

    def test_cron_imports_other_journals_when_one_fails(self):
        other_company_data = self.setup_other_company()
        failing_journal = self._create_stripe_journal(other_company_data)
        failing_journal.sequence = 1
        self.stripe_journal.sequence = 99
        self._add_simple_stripe_payout("po_1", 1700000000)

        with self.assertLogs(
            "odoo.addons.account_move_stripe_import.models.account_journal", "ERROR"
        ):
            self._run_stripe_import_cron()

        self.assertEqual(self._stripe_entries().mapped("ref"), ["po_1"])
        self.assertFalse(self._stripe_entries(failing_journal))
