# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import time

from odoo.tests import SavepointCase


class TestReconcileHistoryDisplayItems(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReconcileHistoryDisplayItems, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref('base.res_partner_18')
        cls.partner_2 = cls.partner.copy({'name': 'Test'})
        cls.account_receivable = cls.env['account.account'].search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_receivable').id)
        ], limit=1)
        account_revenue = cls.env['account.account'].search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_revenue').id)
        ], limit=1)
        sales_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale')], limit=1)
        year = time.strftime('%Y')
        # Create invoices for partner (partial reconcile)
        cls.cust_invoice_january = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'date_invoice': '%s-01-15' % year,
            'account_id': cls.account_receivable.id,
            'journal_id': sales_journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': '[CONS_DEL01] Server',
                'product_id': cls.env.ref('product.consu_delivery_01').id,
                'account_id': account_revenue.id,
                'price_unit': 1500.0,
                'quantity': 1.0,
            })],
        })

        cls.cust_invoice_january.action_invoice_open()
        cls.cust_invoice_january.move_id.write({
            'ref': 'test_reconcile_partial'
        })
        cls.cust_invoice_february = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'date_invoice': '%s-02-15' % year,
            'account_id': cls.account_receivable.id,
            'journal_id': sales_journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': '[CONS_DEL01] Server',
                'product_id': cls.env.ref('product.consu_delivery_01').id,
                'account_id': account_revenue.id,
                'price_unit': 1500.0,
                'quantity': 1.0,
            })],
        })
        cls.cust_invoice_february.action_invoice_open()
        cls.cust_invoice_february.move_id.write({
            'ref': 'test_reconcile_partial'
        })
        # Create invoice for partner 2 (full reconcile)
        cls.cust_invoice_partner_2 = cls.cust_invoice_january.copy({
            'partner_id': cls.partner_2.id
        })
        cls.cust_invoice_partner_2.action_invoice_open()
        cls.cust_invoice_partner_2.move_id.write({
            'ref': 'test_reconcile_full'
        })

    def test_reconcile_history(self):
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)

        # Create payment for partner 1
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': bank_journal.id,
            'amount': 2000.0,
            'communication': 'test_reconcile_partial',
            'payment_method_id': self.env['account.payment.method'].search([
                ('name', '=', 'Manual')], limit=1).id,
        })
        payment.post()
        # Create payment for partner 2
        payment_2 = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_2.id,
            'journal_id': bank_journal.id,
            'amount': 1500.0,
            'communication': 'test_reconcile_full',
            'payment_method_id': self.env['account.payment.method'].search([
                ('name', '=', 'Manual')], limit=1).id,
        })
        payment_2.post()
        reconcile = self.env['account.mass.reconcile'].create({
            'name': 'Test reconcile display',
            'account': self.account_receivable.id,
            'reconcile_method': [(0, 0, {
                'name': 'mass.reconcile.advanced.ref',
                'date_base_on': 'newest',
            })]
        })
        reconcile.run_reconcile()
        # Check full reconciliation for partner 2
        invoice_2_moves = self.cust_invoice_partner_2.move_id.line_ids
        payment_2_move_lines = self.env['account.move.line'].search([
            ('payment_id', '=', payment_2.id)
        ])
        full_reconciled_moves = invoice_2_moves | payment_2_move_lines
        full_reconciled_move_ids = full_reconciled_moves.filtered(
            lambda m: m.account_id == self.account_receivable
        ).ids

        history_full_action = reconcile.last_history_reconcile()
        history_full_lines_ids = history_full_action.get('domain')[0][2]
        self.assertEqual(
            set(full_reconciled_move_ids), set(history_full_lines_ids)
        )
        # Check partial reconciliation for partner 1
        invoice_january_moves = self.cust_invoice_january.move_id.line_ids
        invoice_february_moves = self.cust_invoice_february.move_id.line_ids
        payment_move_lines = self.env['account.move.line'].search([
            ('payment_id', '=', payment.id)
        ])
        reconciled_moves = (
            invoice_january_moves | invoice_february_moves | payment_move_lines
        )
        reconciled_move_ids = reconciled_moves.filtered(
            lambda m: m.account_id == self.account_receivable
        ).ids
        history_partial_action = reconcile.last_history_partial_reconcile()
        history_partial_lines_ids = history_partial_action.get('domain')[0][2]
        self.assertEqual(
            set(reconciled_move_ids), set(history_partial_lines_ids)
        )
