# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestAccountReconcileRefDeepSearch(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountReconcileRefDeepSearch, cls).setUpClass()

        cls.partner = cls.env.ref('base.res_partner_18')
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
        # Create invoice
        cls.cust_invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'account_id': cls.account_receivable.id,
            'journal_id': sales_journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': '[CONS_DEL01] Server',
                'product_id': cls.env.ref('product.consu_delivery_01').id,
                'account_id': account_revenue.id,
                'price_unit': 1000.0,
                'quantity': 1.0,
            })],
            'name': 'test_deep_search'
        })
        cls.cust_invoice.action_invoice_open()

    def test_account_reconcile_ref_deep_search(self):
        self.assertEqual(self.cust_invoice.state, 'open')
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)

        # Create payment
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': bank_journal.id,
            'amount': 1000.0,
            'communication': 'test_deep_search',
            'payment_method_id': self.env['account.payment.method'].search([
                ('name', '=', 'Manual')], limit=1).id,
        })
        self.assertEqual(payment.state, 'draft')
        payment.post()
        self.assertEqual(payment.state, 'posted')

        reconcile = self.env['account.mass.reconcile'].create({
            'name': 'Test reconcile ref deep search',
            'account': self.account_receivable.id,
            'reconcile_method': [(0, 0, {
                'name': 'mass.reconcile.advanced.ref.deep.search',
                'date_base_on': 'newest',
            })]
        })
        count = reconcile.unreconciled_count
        reconcile.run_reconcile()
        self.assertEqual(self.cust_invoice.state, 'paid')
        self.assertEqual(reconcile.unreconciled_count, count - 2)
