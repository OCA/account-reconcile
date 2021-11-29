# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime
from odoo.modules import get_resource_path
from odoo.tests import SingleTransactionCase
from odoo.tools import convert_file


class TestCompletionTransactionId(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        convert_file(
            cls.cr,
            'account',
            get_resource_path('account', 'test', 'account_minimal_test.xml'),
            {},
            'init',
            False,
            'test',
        )
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.journal = cls.env.ref('account.bank_journal')
        cls.journal.used_for_completion = True
        cls.move = cls.env['account.move'].create(
            {'name': 'Move with transaction ID', 'journal_id': cls.journal.id}
        )
        cls.move_line = cls.env['account.move.line'].create(
            {
                'name': 'Test autocompletion on invoice with transaction ID',
                'account_id': cls.env.ref('account.a_sale').id,
                'move_id': cls.move.id,
                'ref': 'XXX66Z',
                'date_maturity': '{}-01-06'.format(datetime.now().year),
                'credit': 0.0,
            }
        )

    def test_sale_order_transaction_id(self):
        self.move_line.ref = 'XXX66Z'
        self.journal.rule_ids = [
            (
                4,
                self.env.ref(
                    'account_move_transactionid_import.'
                    'bank_statement_completion_rule_4'
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    'account_move_base_import.bank_statement_completion_rule_2'
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    'account_move_base_import.bank_statement_completion_rule_3'
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    'account_move_base_import.bank_statement_completion_rule_4'
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    'account_move_base_import.bank_statement_completion_rule_5'
                ).id,
                False,
            ),
        ]
        self.move_line.with_context({'check_move_validity': False}).write(
            {'credit': 118.4}
        )
        so = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'note': 'Invoice after delivery',
                'transaction_id': 'XXX66Z',
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'product_id': self.env.ref(
                                'product.product_product_7'
                            ).id,
                            'product_uom_qty': 8,
                        },
                    )
                ],
            }
        )
        self.assertEqual(so.transaction_id, 'XXX66Z')
        self.move.button_auto_completion()
        self.assertEqual(self.move_line.partner_id.name, self.partner.name)

    def test_new_invoice_with_transaction_id(self):
        self.move_line.ref = 'XXX77Z'
        self.move_line.partner_id = None
        self.journal.rule_ids = [
            (
                4,
                self.env.ref(
                    'account_move_transactionid_import.'
                    'bank_statement_completion_rule_trans_id_invoice'
                ).id,
                False,
            )
        ]
        invoice = self.env['account.invoice'].create(
            {
                'currency_id': self.env.ref('base.EUR').id,
                'partner_id': self.partner.id,
                'transaction_id': 'XXX77Z',
                'reference_type': 'none',
                'journal_id': self.journal.id,
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': '[PCSC234] PC Assemble SC234',
                            'price_unit': 450.0,
                            'quantity': 1.0,
                            'product_id': self.env.ref(
                                'product.product_product_3'
                            ).id,
                            'uom_id': self.env.ref('uom.product_uom_unit').id,
                            'account_id': self.env.ref('account.a_sale').id,
                        },
                    )
                ],
            }
        )
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'open')
        self.move.button_auto_completion()
        self.assertEqual(self.move_line.partner_id, self.partner)
