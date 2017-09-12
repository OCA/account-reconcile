# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


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
