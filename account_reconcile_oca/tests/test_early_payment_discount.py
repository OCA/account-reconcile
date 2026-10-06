# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import Form, tagged

from .test_bank_account_reconcile import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestReconcileEarlyPaymentDiscount(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice_date = fields.Date.from_string("2026-01-01")
        cls.discount_loss_account = (
            cls.company.account_journal_early_pay_discount_loss_account_id
        )
        cls.discount_gain_account = (
            cls.company.account_journal_early_pay_discount_gain_account_id
        )
        cls.tax_sale_19 = cls.env["account.tax"].create(
            {
                "name": "Sale 19%",
                "amount_type": "percent",
                "amount": 19.0,
                "type_tax_use": "sale",
            }
        )
        cls.tax_purchase_19 = cls.env["account.tax"].create(
            {
                "name": "Purchase 19%",
                "amount_type": "percent",
                "amount": 19.0,
                "type_tax_use": "purchase",
            }
        )
        cls.payment_term_epd = cls._create_epd_payment_term(2, 10)
        # A second term to check that a single model handles every payment term
        cls.payment_term_epd_3 = cls._create_epd_payment_term(3, 14)
        cls.invoice_matching_model = cls.env["account.reconcile.model"].create(
            {
                "name": "Invoice matching",
                "rule_type": "invoice_matching",
                "match_partner": True,
                "auto_reconcile": False,
                "allow_payment_tolerance": False,
            }
        )

    @classmethod
    def _create_epd_payment_term(cls, discount_percentage, discount_days):
        return cls.env["account.payment.term"].create(
            {
                "name": f"{discount_percentage}% within {discount_days} days, net 30",
                "early_discount": True,
                "discount_percentage": discount_percentage,
                "discount_days": discount_days,
                "early_pay_discount_computation": "included",
                "line_ids": [
                    Command.create(
                        {"value": "percent", "value_amount": 100, "nb_days": 30}
                    )
                ],
            }
        )

    def _disable_invoice_matching_models(self):
        self.env["account.reconcile.model"].search(
            [("rule_type", "=", "invoice_matching")]
        ).active = False

    def _create_epd_invoice(
        self, move_type="out_invoice", price_unit=100.0, payment_term=None, tax=None
    ):
        if tax is None:
            tax = (
                self.tax_sale_19 if move_type == "out_invoice" else self.tax_purchase_19
            )
        invoice = self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner_agrolait.id,
                "invoice_date": self.invoice_date,
                "date": self.invoice_date,
                "invoice_payment_term_id": (payment_term or self.payment_term_epd).id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "line",
                            "price_unit": price_unit,
                            "tax_ids": [Command.set(tax.ids)],
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _create_st_line(self, amount, invoice, date="2026-01-05", **kwargs):
        return self.acc_bank_stmt_line_model.create(
            {
                "journal_id": self.bank_journal_euro.id,
                "payment_ref": invoice.name,
                "partner_id": self.partner_agrolait.id,
                "amount": amount,
                "date": date,
                **kwargs,
            }
        )

    def _epd_reconcile_lines(self, st_line):
        return [
            line
            for line in st_line.reconcile_data_info["data"]
            if line.get("display_type") == "epd"
        ]

    def _assert_bank_amount_open(self, st_line):
        """Only the statement line and its full counterpart are left"""
        data = st_line.reconcile_data_info["data"]
        self.assertFalse(self._epd_reconcile_lines(st_line))
        self.assertEqual(
            [(line["kind"], line["amount"]) for line in data],
            [("liquidity", 116.62), ("suspense", -116.62)],
        )

    def test_invoice_matching_with_discount(self):
        """119.00 invoice paid 116.62 within the discount period"""
        invoice = self._create_epd_invoice()
        self.assertEqual(invoice.amount_total, 119.0)
        st_line = self._create_st_line(116.62, invoice)
        self.assertTrue(st_line.can_reconcile)
        epd_lines = self._epd_reconcile_lines(st_line)
        # One base line (discount account) and one tax reduction line
        self.assertEqual(len(epd_lines), 2)
        self.assertAlmostEqual(sum(line["amount"] for line in epd_lines), 2.38)
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")
        self.assertTrue(st_line.is_reconciled)
        move_lines = st_line.move_id.line_ids
        base_line = move_lines.filtered(
            lambda line: line.account_id == self.discount_loss_account
        )
        self.assertEqual(base_line.debit, 2.0)
        self.assertEqual(base_line.display_type, "epd")
        self.assertEqual(base_line.tax_ids, self.tax_sale_19)
        tax_line = move_lines.filtered(
            lambda line: line.tax_repartition_line_id.tax_id == self.tax_sale_19
        )
        self.assertEqual(tax_line.debit, 0.38)

    def test_vendor_bill_matching_with_discount(self):
        bill = self._create_epd_invoice(move_type="in_invoice")
        # No reference: the bill is found from the partner of the statement line
        st_line = self._create_st_line(-116.62, bill, payment_ref="Pay it")
        self.assertTrue(st_line.can_reconcile)
        st_line.reconcile_bank_line()
        self.assertEqual(bill.payment_state, "paid")
        base_line = st_line.move_id.line_ids.filtered(
            lambda line: line.account_id == self.discount_gain_account
        )
        self.assertEqual(base_line.credit, 2.0)

    def test_several_payment_terms_single_model(self):
        """A single invoice matching model handles every payment term"""
        invoice = self._create_epd_invoice(payment_term=self.payment_term_epd_3)
        st_line = self._create_st_line(115.43, invoice)  # 119 - 3%
        self.assertTrue(st_line.can_reconcile)
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")

    def test_no_discount_after_discount_date(self):
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice, date="2026-01-25")
        self.assertFalse(self._epd_reconcile_lines(st_line))
        # Proposed as a partial payment, the discount stays open on the invoice
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "partial")
        self.assertAlmostEqual(invoice.amount_residual, 2.38)

    def test_full_payment_no_discount(self):
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(119.0, invoice)
        self.assertTrue(st_line.can_reconcile)
        self.assertFalse(self._epd_reconcile_lines(st_line))
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")

    def test_auto_reconcile_with_discount(self):
        self.invoice_matching_model.auto_reconcile = True
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice)
        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")

    def test_auto_reconcile_keep_mode_with_discount(self):
        self.bank_journal_euro.reconcile_mode = "keep"
        self.bank_journal_euro.suspense_account_id.reconcile = True
        self.invoice_matching_model.auto_reconcile = True
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice)
        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")
        # The discount lines are in the separate reconciliation entry
        term_line = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        reconcile_move = term_line.matched_credit_ids.credit_move_id.move_id
        self.assertNotEqual(reconcile_move, st_line.move_id)
        move_lines = reconcile_move.line_ids
        base_line = move_lines.filtered(
            lambda line: line.account_id == self.discount_loss_account
        )
        self.assertEqual(base_line.debit, 2.0)
        self.assertEqual(base_line.display_type, "epd")
        tax_line = move_lines.filtered(
            lambda line: line.tax_repartition_line_id.tax_id == self.tax_sale_19
        )
        self.assertEqual(tax_line.debit, 0.38)

    def test_manual_add_with_discount(self):
        self._disable_invoice_matching_models()
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice)
        term_line = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        with Form(
            st_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_account_move_line_id = term_line
            self.assertTrue(f.can_reconcile)
        self.assertEqual(len(self._epd_reconcile_lines(st_line)), 2)
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")

    def test_manual_delete_removes_discount(self):
        """Deleting the journal item removes its early payment discount lines"""
        self._disable_invoice_matching_models()
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice)
        term_line = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        with Form(
            st_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_account_move_line_id = term_line
            self.assertEqual(len(self._epd_reconcile_lines(f)), 2)
            f.manual_reference = f"account.move.line;{term_line.id}"
            f.manual_delete = True
            self._assert_bank_amount_open(f)
        self.assertFalse(self._epd_reconcile_lines(st_line))

    def test_manual_unselect_removes_discount(self):
        """Unselecting the journal item removes its early payment discount lines"""
        self._disable_invoice_matching_models()
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(116.62, invoice)
        term_line = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        with Form(
            st_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_account_move_line_id = term_line
            self.assertEqual(len(self._epd_reconcile_lines(f)), 2)
            f.add_account_move_line_id = term_line
            self._assert_bank_amount_open(f)
        self.assertFalse(self._epd_reconcile_lines(st_line))

    def test_manual_add_partial_without_discount(self):
        """A payment different from the discounted amount stays a partial"""
        self._disable_invoice_matching_models()
        invoice = self._create_epd_invoice()
        st_line = self._create_st_line(50.0, invoice)
        term_line = invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        )
        with Form(
            st_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_account_move_line_id = term_line
            self.assertTrue(f.can_reconcile)
        self.assertFalse(self._epd_reconcile_lines(st_line))
        st_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "partial")
        self.assertEqual(invoice.amount_residual, 69.0)
