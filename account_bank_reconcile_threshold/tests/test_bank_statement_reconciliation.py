# -*- coding: utf-8 -*-
# Copyright 2018 Odoo SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestBankStatementReconciliation(AccountingTestCase):

    def setUp(self):
        super(TestBankStatementReconciliation, self).setUp()
        self.i_model = self.env['account.invoice']
        self.il_model = self.env['account.invoice.line']
        self.bs_model = self.env['account.bank.statement']
        self.bsl_model = self.env['account.bank.statement.line']
        self.partner_agrolait = self.env.ref("base.res_partner_2")

    def test_reconciliation_proposition(self):
        rcv_mv_line = self.create_invoice('1900-01-01', 100)
        rcv_mv_line2 = self.create_invoice('2010-01-01', 100)
        rcv_mv_line.company_id.account_bank_reconciliation_start = '2000-01-01'
        st_line = self.create_statement_line(100)

        # exact amount match
        aml = st_line.get_move_lines_for_reconciliation()
        self.assertTrue(rcv_mv_line not in aml)
        self.assertTrue(rcv_mv_line2 in aml)

    def create_invoice(self, date, amount):
        vals = {'partner_id': self.partner_agrolait.id,
                'type': 'out_invoice',
                'name': '-',
                'date_invoice': date,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
        # new creates a temporary record to apply the on_change afterwards
        invoice = self.i_model.new(vals)
        invoice._onchange_partner_id()
        vals.update({'account_id': invoice.account_id.id})
        invoice = self.i_model.create(vals)

        self.il_model.create({
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': '.',
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_revenue').id)], limit=1).id,
        })
        invoice.action_invoice_open()

        mv_line = None
        for l in invoice.move_id.line_ids:
            if l.account_id.id == vals['account_id']:
                mv_line = l
        self.assertIsNotNone(mv_line)

        return mv_line

    def create_statement_line(self, st_line_amount):
        journal = self.bs_model.with_context(
            journal_type='bank')._default_journal()
        bank_stmt = self.bs_model.create({'journal_id': journal.id})

        bank_stmt_line = self.bsl_model.create({
            'name': '_',
            'statement_id': bank_stmt.id,
            'partner_id': self.partner_agrolait.id,
            'amount': st_line_amount,
            })

        return bank_stmt_line
