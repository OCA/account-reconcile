from freezegun import freeze_time

from odoo import Command, fields
from odoo.tests import tagged

from .test_bank_account_reconcile import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestEarlyPaymentDiscount(TestAccountReconciliationCommon):
    @freeze_time("2019-01-10")
    def test_default_reconcile_data_uses_epd_if_eligible(self):
        partner = self.env["res.partner"].create({"name": "EPD Partner"})
        usd_currency = self.env["res.currency"].browse(self.currency_usd_id)

        epd_payment_term = self.env["account.payment.term"].create(
            {
                "name": "10% discount if paid within 10 days",
                "early_discount": True,
                "discount_percentage": 10.0,
                "discount_days": 10,
                "line_ids": [
                    Command.create(
                        {
                            "value": "percent",
                            "value_amount": 100,
                            "nb_days": 30,
                        }
                    )
                ],
            }
        )

        self.env["account.reconcile.model"].create(
            {
                "name": "EPD invoice matching",
                "sequence": 1,
                "rule_type": "invoice_matching",
                "match_partner": True,
                "match_partner_ids": [Command.set(partner.ids)],
                "match_text_location_label": True,
                "match_text_location_reference": False,
                "match_text_location_note": False,
                "allow_payment_tolerance": True,
                "payment_tolerance_type": "percentage",
                "payment_tolerance_param": 0.0,
                "match_same_currency": True,
                "past_months_limit": False,
                "company_id": self.company.id,
            }
        )

        invoice = self._create_invoice(
            move_type="out_invoice",
            invoice_amount=100.0,
            currency_id=self.currency_usd_id,
            partner_id=partner.id,
            payment_term_id=epd_payment_term.id,
            date_invoice="2019-01-01",
            auto_validate=True,
        )
        receivable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )
        self.assertEqual(len(receivable_line), 1)
        self.assertTrue(receivable_line.name)
        self.assertTrue(receivable_line.discount_date)
        self.assertEqual(
            receivable_line.discount_date.strftime("%Y-%m-%d"), "2019-01-11"
        )
        self.assertTrue(receivable_line.discount_amount_currency)

        company_amount = usd_currency._convert(
            90.0,
            self.company.currency_id,
            self.company,
            fields.Date.from_string("2019-01-10"),
        )

        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "journal_id": self.bank_journal_euro.id,
                "date": "2019-01-10",
                "name": "epd-test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "epd-line",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": company_amount,
                "foreign_currency_id": usd_currency.id,
                "amount_currency": 90.0,
                "date": "2019-01-10",
                "payment_ref": receivable_line.name,
                "partner_id": partner.id,
            }
        )

        reconcile_data = bank_stmt_line._default_reconcile_data()

        counterpart_lines = [
            line
            for line in reconcile_data["data"]
            if receivable_line.id in line.get("counterpart_line_ids", [])
        ]
        self.assertTrue(counterpart_lines)
