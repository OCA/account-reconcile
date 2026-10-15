# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestDraftMoveUnreconcile(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.bank_journal = cls.company_data["default_journal_bank"]
        # Keep invoice totals equal to the given amounts
        cls.company_data["company"].account_sale_tax_id = False
        cls.company_data["default_account_revenue"].tax_ids = False

    def _create_invoice(self, amount):
        return self.init_invoice(
            "out_invoice", partner=self.partner_a, amounts=[amount], post=True
        )

    def _create_statement(self, amounts):
        statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": "2019-01-01",
                "balance_end_real": sum(amounts),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "payment_ref": "Line %s" % i,
                            "partner_id": self.partner_a.id,
                            "amount": amount,
                        },
                    )
                    for i, amount in enumerate(amounts)
                ],
            }
        )
        statement.button_post()
        return statement

    def _reconcile(self, st_line, move_lines):
        st_line.process_reconciliation(
            counterpart_aml_dicts=[
                {
                    "name": line.move_id.name,
                    "debit": -line.amount_residual if line.balance < 0 else 0.0,
                    "credit": line.amount_residual if line.balance > 0 else 0.0,
                    "move_line": line,
                }
                for line in move_lines
            ]
        )

    def _receivable_line(self, move):
        return move.line_ids.filtered(
            lambda line: line.account_id.internal_type == "receivable"
        )

    def _number_to_reconcile(self):
        # The dashboard and the widget read the statement lines with SQL queries
        self.env["base"].flush()
        return self.bank_journal.get_journal_dashboard_datas()["number_to_reconcile"]

    def _count_move_links(self, body):
        return body.count('data-oe-model="account.move"')

    def _pending_st_line_ids(self, statement):
        self.env["base"].flush()
        data = self.env["account.reconciliation.widget"].get_bank_statement_data(
            statement.line_ids.ids
        )
        return [line["st_line"]["id"] for line in data.get("lines", [])]

    def test_invoice_draft(self):
        invoice = self._create_invoice(100.0)
        statement = self._create_statement([100.0])
        st_line = statement.line_ids
        self._reconcile(st_line, self._receivable_line(invoice))
        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 0)

        invoice.button_draft()

        self.assertEqual(invoice.state, "draft")
        self.assertFalse(st_line.is_reconciled)
        self.assertEqual(st_line.amount_residual, -100.0)
        self.assertEqual(self._number_to_reconcile(), 1)
        self.assertEqual(self._pending_st_line_ids(statement), st_line.ids)
        message = statement.message_ids[0]
        self.assertIn(invoice.name, message.body)
        self.assertIn(st_line.payment_ref, message.body)
        self.assertEqual(self._count_move_links(message.body), 1)

    def test_statement_line_with_several_invoices(self):
        invoice_1 = self._create_invoice(100.0)
        invoice_2 = self._create_invoice(200.0)
        statement = self._create_statement([300.0])
        st_line = statement.line_ids
        self._reconcile(
            st_line,
            self._receivable_line(invoice_1) | self._receivable_line(invoice_2),
        )
        self.assertTrue(st_line.is_reconciled)

        invoice_1.button_draft()

        self.assertFalse(st_line.is_reconciled)
        self.assertEqual(st_line.amount_residual, -300.0)
        # The statement line can only be reconciled as a whole by the widget:
        # the other invoice is not paid by this statement line anymore.
        self.assertEqual(invoice_2.state, "posted")
        self.assertEqual(invoice_2.payment_state, "not_paid")
        body = statement.message_ids[0].body
        self.assertIn(invoice_1.name, body)
        self.assertIn(invoice_2.name, body)
        self.assertEqual(self._count_move_links(body), 2)

    def test_several_moves_at_once(self):
        invoice_1 = self._create_invoice(100.0)
        invoice_2 = self._create_invoice(200.0)
        invoice_3 = self._create_invoice(300.0)
        invoice_4 = self._create_invoice(400.0)
        statement = self._create_statement([100.0, 200.0, 700.0])
        st_line_1, st_line_2, st_line_3 = statement.line_ids.sorted("amount")
        self._reconcile(st_line_1, self._receivable_line(invoice_1))
        self._reconcile(st_line_2, self._receivable_line(invoice_2))
        self._reconcile(
            st_line_3,
            self._receivable_line(invoice_3) | self._receivable_line(invoice_4),
        )
        messages = statement.message_ids

        (invoice_1 | invoice_3 | invoice_4).button_draft()

        self.assertFalse(st_line_1.is_reconciled)
        self.assertTrue(st_line_2.is_reconciled)
        self.assertFalse(st_line_3.is_reconciled)
        self.assertEqual(invoice_2.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 2)
        new_messages = statement.message_ids - messages
        self.assertEqual(len(new_messages), 2)
        body_3 = new_messages.filtered(lambda m: invoice_3.name in m.body).body
        self.assertIn(invoice_4.name, body_3)
        # Both invoices are reset to draft: no other reconciliation is undone
        self.assertEqual(self._count_move_links(body_3), 2)
        self.assertEqual(body_3.count("<br>"), 0)

    def test_reconcile_again(self):
        invoice = self._create_invoice(100.0)
        statement = self._create_statement([100.0])
        st_line = statement.line_ids
        self._reconcile(st_line, self._receivable_line(invoice))
        invoice.button_draft()
        self.assertFalse(st_line.is_reconciled)

        invoice.action_post()
        self._reconcile(st_line, self._receivable_line(invoice))

        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(self._number_to_reconcile(), 0)
        statement.button_validate()
        self.assertEqual(statement.state, "confirm")

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
            lambda line: line.account_id == self.bank_journal.payment_debit_account_id
        )
        statement = self._create_statement([100.0])
        st_line = statement.line_ids
        self._reconcile(st_line, outstanding_line)
        self.assertTrue(st_line.is_reconciled)

        payment.action_draft()

        self.assertFalse(st_line.is_reconciled)
        self.assertIn(payment.move_id.name, statement.message_ids[0].body)

    def test_validated_statement(self):
        invoice = self._create_invoice(100.0)
        statement = self._create_statement([100.0])
        self._reconcile(statement.line_ids, self._receivable_line(invoice))
        statement.button_validate()
        self.assertEqual(statement.state, "confirm")

        invoice.button_draft()

        self.assertEqual(statement.state, "posted")
        self.assertFalse(statement.line_ids.is_reconciled)
        self.assertEqual(self._pending_st_line_ids(statement), statement.line_ids.ids)

    def test_statement_reopen(self):
        """Resetting the statement entries themselves (statement reopen) is
        already handled by the standard flow."""
        invoice = self._create_invoice(100.0)
        statement = self._create_statement([100.0])
        self._reconcile(statement.line_ids, self._receivable_line(invoice))
        statement.button_validate()
        messages = statement.message_ids

        statement.button_reopen()

        self.assertEqual(statement.state, "open")
        self.assertFalse(
            (statement.message_ids - messages).filtered(
                lambda m: invoice.name in (m.body or "")
            )
        )

    def test_unrelated_draft(self):
        invoice = self._create_invoice(100.0)
        other_invoice = self._create_invoice(50.0)
        statement = self._create_statement([100.0])
        self._reconcile(statement.line_ids, self._receivable_line(invoice))
        messages = statement.message_ids

        other_invoice.button_draft()

        self.assertTrue(statement.line_ids.is_reconciled)
        self.assertEqual(statement.message_ids, messages)
