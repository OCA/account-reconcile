# © 2014-2016 Camptocamp SA (Damien Crier)
# © 2023 FactorLibre - Aritz Olea <aritz.olea@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

import odoo.tests
from odoo import fields

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestScenarioReconcile(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rec_history_obj = cls.env["mass.reconcile.history"]
        cls.mass_rec_obj = cls.env["account.mass.reconcile"]
        cls.invoice_obj = cls.env["account.move"]
        cls.bk_stmt_obj = cls.env["account.bank.statement"]
        cls.bk_stmt_line_obj = cls.env["account.bank.statement.line"]
        cls.acc_move_line_obj = cls.env["account.move.line"]
        cls.mass_rec_method_obj = cls.env["account.mass.reconcile.method"]
        cls.acs_model = cls.env["res.config.settings"]

        cls.company = cls.company_data["company"]
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.sale_journal = cls.company_data["default_journal_sale"]
        acs_ids = cls.acs_model.search([("company_id", "=", cls.company.id)])

        values = {"group_multi_currency": True}

        if acs_ids:
            acs_ids.write(values)
        else:
            default_vals = cls.acs_model.default_get([])
            default_vals.update(values)
            acs_ids = cls.acs_model.create(default_vals)

    def test_scenario_reconcile(self):
        invoice = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            post=True,
        )
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
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)

    def test_scenario_reconcile_newest(self):
        invoice = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            post=True,
        )
        self.assertEqual("posted", invoice.state)

        receivalble_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payments
        payment_old = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2023-10-01"),
            }
        )
        payment_new = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2023-10-20"),
            }
        )
        payment_old.action_post()
        payment_new.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.simple.partner",
                            "date_base_on": "newest",
                        },
                    )
                ],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)
        self.assertTrue(mass_rec.last_history)
        payment_new_line = payment_new.move_id.line_ids.filtered(
            lambda line: line.credit
        )
        payment_old_line = payment_old.move_id.line_ids.filtered(
            lambda line: line.credit
        )
        self.assertTrue(payment_new_line in mass_rec.last_history.reconcile_line_ids)
        self.assertTrue(payment_new_line.reconciled)
        self.assertFalse(payment_old_line in mass_rec.last_history.reconcile_line_ids)
        self.assertFalse(payment_old_line.reconciled)

    def test_scenario_reconcile_oldest(self):
        invoice = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            post=True,
        )
        self.assertEqual("posted", invoice.state)

        receivalble_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payments
        payment_old = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2023-10-01"),
            }
        )
        payment_new = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2023-10-20"),
            }
        )
        payment_old.action_post()
        payment_new.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.simple.partner",
                            "date_base_on": "oldest",
                        },
                    )
                ],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)
        self.assertTrue(mass_rec.last_history)
        payment_new_line = payment_new.move_id.line_ids.filtered(
            lambda line: line.credit
        )
        payment_old_line = payment_old.move_id.line_ids.filtered(
            lambda line: line.credit
        )
        self.assertFalse(payment_new_line in mass_rec.last_history.reconcile_line_ids)
        self.assertFalse(payment_new_line.reconciled)
        self.assertTrue(payment_old_line in mass_rec.last_history.reconcile_line_ids)
        self.assertTrue(payment_old_line.reconciled)

    def test_scenario_reconcile_currency(self):
        currency_rate = (
            self.env["res.currency.rate"]
            .sudo()
            .search(
                [
                    ("currency_id", "=", self.ref("base.USD")),
                    ("company_id", "=", self.ref("base.main_company")),
                ]
            )
            .filtered(lambda r: r.name == fields.Date.today())
        )
        if not currency_rate:
            # create currency rate
            self.env["res.currency.rate"].create(
                {
                    "name": fields.Date.today(),
                    "currency_id": self.ref("base.USD"),
                    "rate": 1.5,
                }
            )
        else:
            currency_rate = fields.first(currency_rate)
            currency_rate.rate = 1.5
        # create invoice
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "currency_id": self.env.ref("base.USD").id,
                "partner_id": self.partner_a.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test",
                            "quantity": 1,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        self.assertEqual("posted", invoice.state)

        self.env["res.currency.rate"].create(
            {
                "name": fields.Date.today() - timedelta(days=3),
                "currency_id": self.ref("base.USD"),
                "rate": 2,
            }
        )
        receivable_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 50.0,
                "currency_id": self.ref("base.USD"),
                "journal_id": self.bank_journal.id,
                "date": fields.Date.today() - timedelta(days=2),
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)

    def test_scenario_reconcile_partial(self):
        invoice1 = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            post=True,
        )
        invoice1.ref = "test ref"
        # create payment
        receivable_account_id = invoice1.partner_id.property_account_receivable_id.id
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice1.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 500.0,
                "journal_id": self.bank_journal.id,
                "memo": "test ref",
            }
        )
        payment.action_post()
        line_payment = payment.move_id.line_ids.filtered(
            lambda line: line.account_id.id == receivable_account_id
        )
        self.assertEqual(line_payment.reconciled, False)
        invoice1_line = invoice1.line_ids.filtered(
            lambda line: line.account_id.id == receivable_account_id
        )
        self.assertEqual(invoice1_line.reconciled, False)

        # Create the mass reconcile record
        reconcile_method_vals = {
            "name": "mass.reconcile.advanced.ref",
            "write_off": 0.1,
        }
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": receivable_account_id,
                "reconcile_method": [(0, 0, reconcile_method_vals)],
            }
        )
        mass_rec.run_reconcile()

        self.assertEqual(line_payment.amount_residual, -450.0)
        self.assertEqual(invoice1_line.reconciled, True)
        invoice2 = self.init_invoice(move_type="out_invoice", amounts=[500], post=True)
        invoice2.ref = "test ref"
        invoice2_line = invoice2.line_ids.filtered(
            lambda line: line.account_id.id == receivable_account_id
        )
        mass_rec.run_reconcile()
        self.assertEqual(line_payment.reconciled, True)
        self.assertEqual(invoice2_line.reconciled, False)

        self.assertEqual(invoice2_line.amount_residual, 50.0)

    def test_reconcile_with_writeoff(self):
        invoice = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            post=True,
        )

        receivable_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 50.1,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.simple.partner",
                            "account_lost_id": self.company_data[
                                "default_account_expense"
                            ].id,
                            "account_profit_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "journal_id": self.company_data["default_journal_misc"].id,
                            "write_off": 0.05,
                        },
                    )
                ],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("not_paid", invoice.payment_state)
        mass_rec.reconcile_method.write_off = 0.11
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)
        full_reconcile = invoice.line_ids.mapped("full_reconcile_id")
        writeoff_line = full_reconcile.reconciled_line_ids.filtered(
            lambda line: line.debit == 0.1
        )
        self.assertEqual(len(writeoff_line), 1)
        self.assertEqual(
            writeoff_line.move_id.journal_id.id,
            self.company_data["default_journal_misc"].id,
        )

    def test_reconcile_with_writeoff_today(self):
        yesterday = date.today() - timedelta(days=1)
        invoice = self.init_invoice(
            move_type="out_invoice",
            amounts=[50],
            invoice_date=yesterday,
            post=True,
        )

        receivable_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 50.02,
                "journal_id": self.bank_journal.id,
                "date": yesterday,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account_id": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.simple.partner",
                            "account_lost_id": self.company_data[
                                "default_account_expense"
                            ].id,
                            "account_profit_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "journal_id": self.company_data["default_journal_misc"].id,
                            "write_off": 0.05,
                            "date_base_on": "actual",
                        },
                    )
                ],
            }
        )
        # call the automatic reconciliation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)
        full_reconcile = invoice.line_ids.mapped("full_reconcile_id")
        writeoff_line = full_reconcile.reconciled_line_ids.filtered(
            lambda line: line.debit == 0.02
        )
        self.assertEqual(len(writeoff_line), 1)
        self.assertEqual(writeoff_line.date, fields.Date.today())

    def test_reconcile_with_writeoff_currency_opposite_signs(self):
        """Test write-off when company and foreign residuals have opposite signs."""
        self.env.ref("base.group_multi_currency").users |= self.env.user
        self.company.currency_id = self.env.ref("base.EUR")
        usd = self.env.ref("base.USD")
        usd.active = True

        inv_date = fields.Date.today() - timedelta(days=10)
        pay_date = fields.Date.today() - timedelta(days=1)

        # Create currency rates
        self.env["res.currency.rate"].create(
            [
                {
                    "name": inv_date,
                    "currency_id": usd.id,
                    "rate": 1.2,
                    "company_id": self.company.id,
                },
                {
                    "name": pay_date,
                    "rate": 1.25,
                    "currency_id": usd.id,
                    "company_id": self.company.id,
                },
                {
                    "name": fields.Date.today(),
                    "rate": 1.25,
                    "currency_id": usd.id,
                    "company_id": self.company.id,
                },
            ]
        )

        # Create invoice and payment with opposing residual signs
        common_ref = "INV-PAY-OPPOSITE-SIGNS"
        invoice = self.init_invoice(
            move_type="out_invoice",
            partner=self.partner_a,
            currency=usd,
            amounts=[100],
            invoice_date=inv_date,
            post=True,
        )
        invoice.ref = common_ref

        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": self.partner_a.id,
                "destination_account_id": self.company_data[
                    "default_account_receivable"
                ].id,
                "amount": 100.10,
                "currency_id": usd.id,
                "journal_id": self.bank_journal.id,
                "date": pay_date,
                "memo": common_ref,
            }
        )
        payment.action_post()

        # Create and run mass reconciliation
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_currency_writeoff_opposite",
                "account_id": self.company_data["default_account_receivable"].id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.advanced.ref",
                            "account_lost_id": self.company_data[
                                "default_account_expense"
                            ].id,
                            "account_profit_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "journal_id": self.company_data["default_journal_misc"].id,
                            "write_off": 3.50,
                            "date_base_on": "newest",
                        },
                    )
                ],
            }
        )
        invoice_receivable_line = invoice.line_ids.filtered(
            lambda li: li.account_type == "asset_receivable"
        )
        mass_rec.run_reconcile()
        self.assertTrue(invoice_receivable_line.full_reconcile_id)
        # invoice line, payment line, writeoff line, rate cucrrency exchange line
        self.assertEqual(
            len(invoice_receivable_line.full_reconcile_id.reconciled_line_ids), 4
        )
        writeoff_receivable_line = (
            invoice_receivable_line.full_reconcile_id.reconciled_line_ids.filtered(
                lambda li: li.journal_id.id
                == self.company_data["default_journal_misc"].id
            )
        )
        self.assertEqual(
            writeoff_receivable_line.move_id.currency_id,
            usd,
            "USD should be the write-off currency",
        )
        self.assertAlmostEqual(writeoff_receivable_line.amount_currency, 0.1)
