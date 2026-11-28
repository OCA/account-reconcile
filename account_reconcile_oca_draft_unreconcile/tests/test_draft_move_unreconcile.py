# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestDraftMoveUnreconcile(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.bank_journal = cls.company_data["default_journal_bank"]
        # Avoid automatic proposals of the reconciliation models
        cls.env["account.reconcile.model"].search(
            [("company_id", "=", cls.company_data["company"].id)]
        ).active = False
        # Keep invoice totals equal to the given amounts
        cls.company_data["company"].account_sale_tax_id = False
        cls.company_data["default_account_revenue"].tax_ids = False

    def _create_invoice(self, amount):
        return self.init_invoice(
            "out_invoice", partner=self.partner_a, amounts=[amount], post=True
        )

    def _create_st_lines(self, amounts):
        statement = self.env["account.bank.statement"].create(
            {
                "name": "Statement",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "journal_id": self.bank_journal.id,
                            "date": "2019-01-01",
                            "payment_ref": "Line %s" % i,
                            "partner_id": self.partner_a.id,
                            "amount": amount,
                        },
                    )
                    for i, amount in enumerate(amounts)
                ],
            }
        )
        return statement.line_ids.sorted("amount")

    def _reconcile(self, st_line, move_lines):
        with Form(
            st_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as form:
            for line in move_lines:
                form.add_account_move_line_id = line
        st_line.reconcile_bank_line()

    def _receivable_line(self, move):
        return move.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )

    def _number_to_reconcile(self):
        # The dashboard reads the statement lines with SQL queries
        self.env.flush_all()
        return self.bank_journal.get_journal_dashboard_datas()["number_to_reconcile"]

    def _count_move_links(self, body):
        return body.count('data-oe-model="account.move"')

    def _proposed_move_ids(self, st_line):
        st_line.invalidate_recordset()
        return {
            line["move_id"]
            for line in st_line.reconcile_data_info["data"]
            if line.get("move_id") and line["move_id"] != st_line.move_id.id
        }

    def test_invoice_draft(self):
        invoice = self._create_invoice(100.0)
        st_line = self._create_st_lines([100.0])
        self._reconcile(st_line, self._receivable_line(invoice))
        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 0)

        invoice.button_draft()

        self.assertEqual(invoice.state, "draft")
        self.assertFalse(st_line.is_reconciled)
        self.assertEqual(st_line.amount_residual, -100.0)
        self.assertEqual(self._number_to_reconcile(), 1)
        # The reconciliation view does not propose the entry reset to draft
        self.assertFalse(self._proposed_move_ids(st_line))
        message = st_line.move_id.message_ids[0]
        self.assertIn(invoice.name, message.body)
        self.assertIn(st_line.payment_ref, message.body)
        self.assertEqual(self._count_move_links(message.body), 1)

    def test_statement_line_with_several_invoices(self):
        invoice_1 = self._create_invoice(100.0)
        invoice_2 = self._create_invoice(200.0)
        st_line = self._create_st_lines([300.0])
        self._reconcile(
            st_line,
            self._receivable_line(invoice_1) | self._receivable_line(invoice_2),
        )
        self.assertTrue(st_line.is_reconciled)

        invoice_1.button_draft()

        self.assertFalse(st_line.is_reconciled)
        self.assertEqual(st_line.amount_residual, -300.0)
        # The statement line is reconciled as a whole: the other invoice is not
        # paid by this statement line anymore.
        self.assertEqual(invoice_2.state, "posted")
        self.assertEqual(invoice_2.payment_state, "not_paid")
        body = st_line.move_id.message_ids[0].body
        self.assertIn(invoice_1.name, body)
        self.assertIn(invoice_2.name, body)
        self.assertEqual(self._count_move_links(body), 2)

    def test_several_moves_at_once(self):
        invoice_1 = self._create_invoice(100.0)
        invoice_2 = self._create_invoice(200.0)
        invoice_3 = self._create_invoice(300.0)
        invoice_4 = self._create_invoice(400.0)
        st_line_1, st_line_2, st_line_3 = self._create_st_lines([100.0, 200.0, 700.0])
        self._reconcile(st_line_1, self._receivable_line(invoice_1))
        self._reconcile(st_line_2, self._receivable_line(invoice_2))
        self._reconcile(
            st_line_3,
            self._receivable_line(invoice_3) | self._receivable_line(invoice_4),
        )
        messages = st_line_3.move_id.message_ids

        (invoice_1 | invoice_3 | invoice_4).button_draft()

        self.assertFalse(st_line_1.is_reconciled)
        self.assertTrue(st_line_2.is_reconciled)
        self.assertFalse(st_line_3.is_reconciled)
        self.assertEqual(invoice_2.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 2)
        new_messages = st_line_3.move_id.message_ids - messages
        self.assertEqual(len(new_messages), 1)
        body_3 = new_messages.body
        self.assertIn(invoice_3.name, body_3)
        self.assertIn(invoice_4.name, body_3)
        # Both invoices are reset to draft: no other reconciliation is undone
        self.assertEqual(self._count_move_links(body_3), 2)
        self.assertEqual(body_3.count("<br>"), 0)

    def test_reconcile_again(self):
        invoice = self._create_invoice(100.0)
        st_line = self._create_st_lines([100.0])
        self._reconcile(st_line, self._receivable_line(invoice))
        invoice.button_draft()
        self.assertFalse(st_line.is_reconciled)

        invoice.action_post()
        self._reconcile(st_line, self._receivable_line(invoice))

        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 0)

    def test_payment_draft(self):
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_a.id,
                "amount": 100.0,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()
        outstanding_line = payment.line_ids.filtered(
            lambda line: line.account_id != payment.destination_account_id
        )
        st_line = self._create_st_lines([100.0])
        self._reconcile(st_line, outstanding_line)
        self.assertTrue(st_line.is_reconciled)

        payment.action_draft()

        self.assertFalse(st_line.is_reconciled)
        self.assertIn(payment.move_id.name, st_line.move_id.message_ids[0].body)

    def test_unrelated_draft(self):
        invoice = self._create_invoice(100.0)
        other_invoice = self._create_invoice(50.0)
        st_line = self._create_st_lines([100.0])
        self._reconcile(st_line, self._receivable_line(invoice))
        messages = st_line.move_id.message_ids

        other_invoice.button_draft()

        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(st_line.move_id.message_ids, messages)
