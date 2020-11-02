# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo import fields


class TestAccountPayment(common.TransactionCase):

    def test_transaction_id_on_move_line(self):
        account_payment = self.env['account.payment'].new({
            'name': 'payment_name'
        })
        vals = account_payment._get_liquidity_move_line_vals(10)
        self.assertEqual(
            vals.get('name'),
            'payment_name',
            'The name of the move line is the name of the payment if no '
            'transaction_id is specified on the payment')
        account_payment.transaction_id = 'transaction id'
        vals = account_payment._get_liquidity_move_line_vals(10)
        self.assertEqual(
            vals.get('name'),
            'transaction id',
            'The name of the move line is the transaction if of the payment '
            'if specified on the payment')
        self.assertEqual(
            vals.get('transaction_ref'),
            'transaction id',
            'The transaction reference of the move line is the transaction if '
            'of the payment '
            'if specified on the payment')

    def test_transaction_id_from_invoice(self):
        transaction_ref = '1234568787'
        tax = self.env['account.tax'].create({
            'name': 'Tax 10.0',
            'amount': 10.0,
            'amount_type': 'fixed',
        })

        # Should be changed by automatic on_change later
        invoice_account = self.env['account.account'].search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_receivable').id)],
            limit=1).id
        invoice_line_account = self.env['account.account'].search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_expenses').id)],
            limit=1).id

        invoice = self.env['account.invoice'].create(
            {'partner_id': self.env.ref('base.res_partner_2').id,
             'account_id': invoice_account,
             'type': 'out_invoice',
             'transaction_id': transaction_ref})

        self.env['account.invoice.line'].create(
            {'product_id': self.env.ref('product.product_product_4').id,
             'quantity': 1.0,
             'price_unit': 100.0,
             'invoice_id': invoice.id,
             'name': 'product that cost 100',
             'account_id': invoice_line_account,
             'invoice_line_tax_ids': [(6, 0, [tax.id])]})

        # change the state of invoice to open by clicking Validate button
        invoice.action_invoice_open()

        journal = self.env['account.journal'].search([('type', '=', 'bank')],
                                                     limit=1)
        payment = self.env['account.payment'].create({
            'invoice_ids': [(6, 0, invoice.ids)],
            'amount': invoice.residual,
            'payment_date': fields.Date.today(),
            'communication': invoice.reference or invoice.number,
            'partner_id': invoice.partner_id.id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id,
            'payment_type': 'inbound'})
        payment.post()

        self.assertEqual(invoice.state, 'paid')

        move_line = invoice.payment_ids.move_line_ids.filtered(
            lambda x: x.account_id.internal_type == 'liquidity')
        self.assertEqual(move_line.transaction_ref, transaction_ref)
