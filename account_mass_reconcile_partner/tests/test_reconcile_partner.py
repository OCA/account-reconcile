# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import time

from odoo.tests import SavepointCase


class TestAccountReconcilePartner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountReconcilePartner, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
        year = time.strftime('%Y')
        # Create invoice
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
            'name': 'test_reconcile_partner'
        })
        cls.cust_invoice_january.action_invoice_open()

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
            'name': 'test_reconcile_partner'
        })
        cls.cust_invoice_february.action_invoice_open()

    def test_account_reconcile_partner(self):
        self.assertEqual(self.cust_invoice_january.state, 'open')
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)

        # Create payment
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': bank_journal.id,
            'amount': 1000.0,
            'communication': 'test_reconcile',
            'payment_method_id': self.env['account.payment.method'].search([
                ('name', '=', 'Manual')], limit=1).id,
        })
        self.assertEqual(payment.state, 'draft')
        payment.post()
        self.assertEqual(payment.state, 'posted')
        reconcile = self.env['account.mass.reconcile'].create({
            'name': 'Test reconcile partner',
            'account': self.account_receivable.id,
            'reconcile_method': [(0, 0, {
                'name': 'mass.reconcile.advanced.partner',
                'date_base_on': 'newest',
            })]
        })
        reconcile.run_reconcile()

        self.assertEqual(self.cust_invoice_january.residual, 500)
        self.assertEqual(self.cust_invoice_february.residual, 1500)

        # Create payment
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': bank_journal.id,
            'amount': 800.0,
            'communication': 'test_reconcile',
            'payment_method_id': self.env['account.payment.method'].search([
                ('name', '=', 'Manual')], limit=1).id,
        })
        self.assertEqual(payment.state, 'draft')
        payment.post()
        self.assertEqual(payment.state, 'posted')

        reconcile.run_reconcile()
        self.assertEqual(self.cust_invoice_january.residual, 0)
        self.assertEqual(self.cust_invoice_january.state, 'paid')
        self.assertEqual(self.cust_invoice_february.residual, 1200)
        self.assertEqual(self.cust_invoice_february.state, 'open')
