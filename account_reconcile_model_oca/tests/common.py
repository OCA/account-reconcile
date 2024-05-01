import time

from odoo import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountReconciliationCommon(AccountTestInvoicingCommon):

    """Tests for reconciliation (account.tax)

    Test used to check that when doing a sale or purchase invoice in a different
    currency, the result will be balanced.
    """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company = cls.company_data["company"]
        cls.company.currency_id = cls.env.ref("base.EUR")

        cls.partner_agrolait = cls.env["res.partner"].create(
            {
                "name": "Deco Addict",
                "is_company": True,
                "country_id": cls.env.ref("base.us").id,
            }
        )
        cls.partner_agrolait_id = cls.partner_agrolait.id
        cls.currency_swiss_id = cls.env.ref("base.CHF").id
        cls.currency_usd_id = cls.env.ref("base.USD").id
        cls.currency_euro_id = cls.env.ref("base.EUR").id
        cls.account_rcv = cls.company_data["default_account_receivable"]
        cls.account_rsa = cls.company_data["default_account_payable"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Product 4",
                "standard_price": 500.0,
                "list_price": 750.0,
                "type": "consu",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

        cls.bank_journal_euro = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        cls.account_euro = cls.bank_journal_euro.default_account_id

        cls.bank_journal_usd = cls.env["account.journal"].create(
            {
                "name": "Bank US",
                "type": "bank",
                "code": "BNK68",
                "currency_id": cls.currency_usd_id,
            }
        )
        cls.account_usd = cls.bank_journal_usd.default_account_id

        cls.fx_journal = cls.company.currency_exchange_journal_id
        cls.diff_income_account = cls.company.income_currency_exchange_account_id
        cls.diff_expense_account = cls.company.expense_currency_exchange_account_id

        cls.expense_account = cls.company_data["default_account_expense"]
        # cash basis intermediary account
        cls.tax_waiting_account = cls.env["account.account"].create(
            {
                "name": "TAX_WAIT",
                "code": "TWAIT",
                "account_type": "liability_current",
                "reconcile": True,
                "company_id": cls.company.id,
            }
        )
        # cash basis final account
        cls.tax_final_account = cls.env["account.account"].create(
            {
                "name": "TAX_TO_DEDUCT",
                "code": "TDEDUCT",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        cls.tax_base_amount_account = cls.env["account.account"].create(
            {
                "name": "TAX_BASE",
                "code": "TBASE",
                "account_type": "asset_current",
                "company_id": cls.company.id,
            }
        )
        cls.company.account_cash_basis_base_account_id = cls.tax_base_amount_account.id

        # Journals
        cls.purchase_journal = cls.company_data["default_journal_purchase"]
        cls.cash_basis_journal = cls.env["account.journal"].create(
            {
                "name": "Test CABA",
                "code": "tCABA",
                "type": "general",
            }
        )
        cls.general_journal = cls.company_data["default_journal_misc"]

        # Tax Cash Basis
        cls.tax_cash_basis = cls.env["account.tax"].create(
            {
                "name": "cash basis 20%",
                "type_tax_use": "purchase",
                "company_id": cls.company.id,
                "country_id": cls.company.account_fiscal_country_id.id,
                "amount": 20,
                "tax_exigibility": "on_payment",
                "cash_basis_transition_account_id": cls.tax_waiting_account.id,
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "account_id": cls.tax_final_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "account_id": cls.tax_final_account.id,
                        },
                    ),
                ],
            }
        )
        cls.env["res.currency.rate"].create(
            [
                {
                    "currency_id": cls.env.ref("base.EUR").id,
                    "name": "2010-01-02",
                    "rate": 1.0,
                },
                {
                    "currency_id": cls.env.ref("base.USD").id,
                    "name": "2010-01-02",
                    "rate": 1.2834,
                },
                {
                    "currency_id": cls.env.ref("base.USD").id,
                    "name": time.strftime("%Y-06-05"),
                    "rate": 1.5289,
                },
            ]
        )

    def _create_invoice(
        self,
        move_type="out_invoice",
        invoice_amount=50,
        currency_id=None,
        partner_id=None,
        date_invoice=None,
        payment_term_id=False,
        auto_validate=False,
    ):
        date_invoice = date_invoice or time.strftime("%Y") + "-07-01"

        invoice_vals = {
            "move_type": move_type,
            "partner_id": partner_id or self.partner_agrolait_id,
            "invoice_date": date_invoice,
            "date": date_invoice,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "product that cost %s" % invoice_amount,
                        "quantity": 1,
                        "price_unit": invoice_amount,
                        "tax_ids": [Command.set([])],
                    },
                )
            ],
        }

        if payment_term_id:
            invoice_vals["invoice_payment_term_id"] = payment_term_id

        if currency_id:
            invoice_vals["currency_id"] = currency_id

        invoice = (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            .create(invoice_vals)
        )
        if auto_validate:
            invoice.action_post()
        return invoice

    def create_invoice(
        self, move_type="out_invoice", invoice_amount=50, currency_id=None
    ):
        return self._create_invoice(
            move_type=move_type,
            invoice_amount=invoice_amount,
            currency_id=currency_id,
            auto_validate=True,
        )

    def create_invoice_partner(
        self,
        move_type="out_invoice",
        invoice_amount=50,
        currency_id=None,
        partner_id=False,
        payment_term_id=False,
    ):
        return self._create_invoice(
            move_type=move_type,
            invoice_amount=invoice_amount,
            currency_id=currency_id,
            partner_id=partner_id,
            payment_term_id=payment_term_id,
            auto_validate=True,
        )
