# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.modules import get_resource_path
from odoo.tests import SingleTransactionCase
from odoo.tools import convert_file


class TestInvoice(SingleTransactionCase):

    def setUp(self):
        super().setUp()
        self.account_move_obj = self.env["account.move"]
        self.account_move_line_obj = \
            self.env["account.move.line"]
        self.company_a = self.env.ref('base.main_company')
        self.partner = self.env.ref("base.res_partner_12")

    def test_01_partner(self):
        # I fill in the field Bank Statement Label in a Partner
        self.partner_4 = self.env.ref('base.res_partner_4')
        self.partner_4.bank_statement_label = 'XXX66Z'
        self.assertEqual(self.partner_4.bank_statement_label, 'XXX66Z')

    def test_02_invoice(self):
        convert_file(
            self.cr, 'account', get_resource_path(
                'account', 'test', 'account_minimal_test.xml'
            ), {}, 'init', False, 'test'
        )
        self.journal = self.env.ref("account.bank_journal")
        self.account_id = self.env.ref("account.a_recv")
        # I create a customer Invoice to be found by the completion.
        product_3 = self.env.ref('product.product_product_3')
        self.invoice_for_completion_1 = self.env['account.invoice'].create({
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': [(0, 0, {
                'name': '[PCSC234] PC Assemble SC234',
                'product_id': product_3.id,
                'price_unit': 210.0,
                'quantity': 1.0,
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'account_id': self.env.ref('account.a_sale').id,
            })],
            'journal_id': self.journal.id,
            'partner_id': self.partner.id,
            'account_id': self.env.ref('account.a_recv').id,
        })
        # I confirm the Invoice
        self.invoice_for_completion_1.action_invoice_open()
        # I check that the invoice state is "Open"
        self.assertEqual(self.invoice_for_completion_1.state, 'open')
        # I check that it is given the number "TBNK/%Y/0001"
        self.assertEqual(
            self.invoice_for_completion_1.number,
            fields.Date.today().strftime('TBNK/%Y/0001')
        )

    def test_03_supplier_invoice(self):
        # I create a demo invoice
        product_delivery = self.env.ref('product.product_delivery_01')
        product_order = self.env.ref('product.product_order_01')
        exp_account = self.env.ref('account.a_expense')
        rec_account = self.env.ref('account.a_recv')
        demo_invoice_0 = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'payment_term_id': self.env.ref('account.account_payment_term').id,
            'type': 'in_invoice',
            'date_invoice': fields.Date.today().replace(day=1),
            'account_id': rec_account.id,
            'invoice_line_ids': [
                (0, 0, {
                    'price_unit': 10.0,
                    'quantity': 1.0,
                    'product_id': product_delivery.id,
                    'name': product_delivery.name,
                    'uom_id': self.env.ref('uom.product_uom_unit').id,
                    'account_id': exp_account.id,
                }), (0, 0, {
                    'price_unit': 4.0,
                    'quantity': 1.0,
                    'product_id': product_order.id,
                    'name': product_order.name,
                    'uom_id': self.env.ref('uom.product_uom_unit').id,
                    'account_id': exp_account.id,
                })
            ],
        })

        # I check that my invoice is a supplier invoice
        self.assertEqual(
            demo_invoice_0.type, 'in_invoice', msg="Check invoice type"
        )
        # I add a reference to an existing supplier invoice
        demo_invoice_0.write({'reference': 'T2S12345'})
        # I check a second time that my invoice is still a supplier invoice
        self.assertEqual(
            demo_invoice_0.type, 'in_invoice', msg="Check invoice type 2"
        )
        # Now I confirm it
        demo_invoice_0.action_invoice_open()
        # I check that the supplier number is there
        self.assertEqual(
            demo_invoice_0.reference, 'T2S12345', msg="Check supplier number"
        )
        # I check a third time that my invoice is still a supplier invoice
        self.assertEqual(
            demo_invoice_0.type, 'in_invoice', msg="Check invoice type 3"
        )

    def test_04_refund(self):
        # I create a "child" partner, to use in the invoice
        # (and have a different commercial_partner_id than itself)
        res_partner_12_child = self.env['res.partner'].create({
            'name': 'Child Partner',
            'supplier': False,
            'customer': True,
            'is_company': False,
            'parent_id': self.partner.id,
        })
        # I create a customer refund to be found by the completion.
        product_3 = self.env.ref('product.product_product_3')
        self.refund_for_completion_1 = self.env['account.invoice'].create({
            'currency_id': self.env.ref('base.EUR').id,
            'invoice_line_ids': [(0, 0, {
                'name': '[PCSC234] PC Assemble SC234',
                'product_id': product_3.id,
                'price_unit': 210.0,
                'quantity': 1.0,
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'account_id': self.env.ref('account.a_sale').id,
            })],
            'journal_id': self.env.ref('account.expenses_journal').id,
            'partner_id': res_partner_12_child.id,
            'type': 'out_refund',
            'account_id': self.env.ref('account.a_recv').id,
        })
        # I confirm the refund
        self.refund_for_completion_1.action_invoice_open()

        # I check that the refund state is "Open"
        self.assertEqual(self.refund_for_completion_1.state, 'open')
        # I check that it is given the number "RTEXJ/%Y/0001"
        self.assertEqual(
            self.refund_for_completion_1.number,
            fields.Date.today().strftime('RTEXJ/%Y/0001')
        )

    def test_05_completion(self):
        # In order to test the banking framework, I first need to create a
        # journal
        self.journal = self.env.ref("account.bank_journal")
        completion_rule_4 = self.env.ref(
            'account_move_base_import.bank_statement_completion_rule_4'
        )
        completion_rule_2 = self.env.ref(
            'account_move_base_import.bank_statement_completion_rule_2'
        )
        completion_rule_3 = self.env.ref(
            'account_move_base_import.bank_statement_completion_rule_3'
        )
        completion_rule_5 = self.env.ref(
            'account_move_base_import.bank_statement_completion_rule_5'
        )
        completion_rules = (
            completion_rule_2 | completion_rule_3 | completion_rule_4
            | completion_rule_5
        )
        self.journal.write({
            'used_for_completion': True,
            'rule_ids': [
                (4, comp_rule.id, False) for comp_rule in completion_rules
            ]
        })
        # Now I create a statement. I create statment lines separately because
        # I need to find each one by XML id
        move_test1 = self.env['account.move'].create({
            'name': 'Move 2',
            'journal_id': self.journal.id,
        })
        # I create a move line for a CI
        move_line_ci = self.env['account.move.line'].create({
            'name': '\\',
            'account_id': self.env.ref('account.a_sale').id,
            'move_id': move_test1.id,
            'date_maturity': fields.Date.from_string('2013-12-20'),
            'credit': 0.0,
        })
        # I create a move line for a SI
        move_line_si = self.env['account.move.line'].create({
            'name': '\\',
            'account_id': self.env.ref('account.a_expense').id,
            'move_id': move_test1.id,
            'date_maturity': fields.Date.from_string('2013-12-19'),
            'debit': 0.0,
        })
        # I create a move line for a CR
        move_line_cr = self.env['account.move.line'].create({
            'name': '\\',
            'account_id': self.env.ref('account.a_expense').id,
            'move_id': move_test1.id,
            'date_maturity': fields.Date.from_string('2013-12-19'),
            'debit': 0.0,
        })
        # I create a move line for the Partner Name
        move_line_partner_name = self.env['account.move.line'].create({
            'name': 'Test autocompletion based on Partner Name Azure Interior',
            'account_id': self.env.ref('account.a_sale').id,
            'move_id': move_test1.id,
            'date_maturity': fields.Date.from_string('2013-12-17'),
            'credit': 0.0,
        })
        # I create a move line for the Partner Label
        move_line_partner_label = self.env['account.move.line'].create({
            'name': 'XXX66Z',
            'account_id': self.env.ref('account.a_sale').id,
            'move_id': move_test1.id,
            'date_maturity': '2013-12-24',
            'debit': 0.0,
        })
        # and add the correct name
        move_line_ci.with_context(check_move_validity=False).write({
            'name': fields.Date.today().strftime('TBNK/%Y/0001'),
            'credit': 210.0,
        })
        move_line_si.with_context(check_move_validity=False).write({
            'name': 'T2S12345',
            'debit': 65.0,
        })
        move_line_cr.with_context(check_move_validity=False).write({
            'name': fields.Date.today().strftime('RTEXJ/%Y/0001'),
            'debit': 210.0,
        })
        move_line_partner_name.with_context(check_move_validity=False).write({
            'credit': 600.0,
        })
        move_line_partner_label.with_context(check_move_validity=False).write({
            'debit': 932.4,
        })
        # I run the auto complete
        move_test1.button_auto_completion()
        # Now I can check that all is nice and shiny, line 1. I expect the
        # Customer Invoice Number to be recognised.
        # I Use _ref, because ref conflicts with the field ref of the
        # statement line
        self.assertEqual(
            move_line_ci.partner_id, self.partner,
            msg="Check completion by CI number"
        )
        # Line 2. I expect the Supplier invoice number to be recognised. The
        # supplier invoice was created by the account module demo data, and we
        # confirmed it here.
        self.assertEqual(
            move_line_si.partner_id, self.partner,
            msg="Check completion by SI number"
        )
        # Line 3. I expect the Customer refund number to be recognised. It
        # should be the commercial partner, and not the regular partner.
        self.assertEqual(
            move_line_cr.partner_id, self.partner,
            msg="Check completion by CR number and commercial partner"
        )
        # Line 4. I check that the partner name has been recognised.
        self.assertEqual(
            move_line_partner_name.partner_id.name, 'Azure Interior',
            msg="Check completion by partner name"
        )
        # Line 5. I check that the partner special label has been recognised.
        self.partner_4 = self.env.ref('base.res_partner_4')
        self.assertEqual(
            move_line_partner_label.partner_id,
            self.partner_4,
            msg="Check completion by partner label"
        )
