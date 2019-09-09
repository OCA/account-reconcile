# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.account_payment_order.tests.test_payment_order_inbound \
    import TestPaymentOrderInboundBase


class TestAccountReconcilePaymentOrder(TestPaymentOrderInboundBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bank_journal = cls.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        # Create second invoice for being sure it handles the payment order
        cls.invoice2 = cls._create_customer_invoice(cls)
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'Test partner 2',
        })
        cls.invoice2.partner_id = cls.partner2.id
        cls.invoice2.action_invoice_open()
        # Add to payment order using the wizard
        cls.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=cls.invoice2.ids,
        ).create({}).run()
        # Prepare statement
        cls.statement = cls.env['account.bank.statement'].create({
            'name': 'Test statement',
            'date': '2019-01-01',
            'journal_id': cls.bank_journal.id,
            'line_ids': [
                (0, 0, {
                    'date': '2019-01-01',
                    'name': 'Test line',
                    'amount': 200,
                }),
            ],
        })
        cls.st_line = cls.statement.line_ids[0]

    def test_reconcile_payment_order_bank(self):
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        self.inbound_mode.write({
            'offsetting_account': 'bank_account',
            'move_option': 'line',
        })
        # Prepare payment order
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        # Check widget result
        res = self.st_line.get_reconciliation_proposition()
        self.assertEqual(len(res), 2)

    def test_reconcile_payment_order_transfer_account(self):
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        receivable_account = self.env['account.account'].create({
            'name': 'Extra receivable account',
            'code': 'TEST_ERA',
            'reconcile': True,
            'user_type_id': (
                self.env.ref('account.data_account_type_receivable').id),
        })
        self.inbound_mode.write({
            'offsetting_account': 'transfer_account',
            'transfer_account_id': receivable_account.id,
            'transfer_journal_id': self.bank_journal.id,
            'move_option': 'line',
        })
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        # Prepare payment order
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        # Check widget result
        res = self.st_line.get_reconciliation_proposition()
        self.assertEqual(len(res), 2)
        # Reconcile that entries and check again
        self.st_line.process_reconciliation(
            counterpart_aml_dicts=[{
                'move_line': res[0],
                'debit': res[0].credit,
                'credit': res[0].debit,
                'name': res[0].name,
            }, {
                'move_line': res[1],
                'debit': res[1].credit,
                'credit': res[1].debit,
                'name': res[1].name,
            }]
        )
        res2 = self.st_line.get_reconciliation_proposition()
        self.assertNotEqual(res, res2)
