# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestAccountBankStatementFilter(common.TransactionCase):

    def setUp(self):
        super(TestAccountBankStatementFilter, self).setUp()

        self.partner_id = self.ref('base.res_partner_2')
        self.account_rcv = self.env.ref('account.a_recv')
        self.bank_journal = self.ref('account.bank_journal')

        self.statement_line_model = self.env['account.bank.statement.line']

        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_id,
            'reference_type': 'none',
            'name': 'invoice to client',
            'account_id': self.account_rcv.id,
            'type': 'out_invoice',
        })
        self.env['account.invoice.line'].create({
            'name': 'product that cost 100.00',
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
        })
        invoice.signal_workflow('invoice_open')

        bank_stmt = self.env['account.bank.statement'].create({
            'journal_id': self.bank_journal,
        })
        self.bank_stmt_line = self.statement_line_model.create({
            'name': 'complete payment',
            'statement_id': bank_stmt.id,
            'partner_id': self.partner_id,
            'amount': 100.00,
        })

    def test_bank_statement_filter_by_account_code(self):
        lines = self.statement_line_model.get_move_lines_for_reconciliation(
            self.bank_stmt_line, str=self.account_rcv.code)
        self.assertTrue(lines, "Not any account move line found.")
        lines = self.statement_line_model.get_move_lines_for_reconciliation(
            self.bank_stmt_line, str=self.account_rcv.code + 'NOT')
        self.assertFalse(lines, "Account move line found.")
