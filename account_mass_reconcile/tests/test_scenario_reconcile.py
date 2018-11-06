# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import fields, tools
from odoo.modules import get_module_resource


class TestScenarioReconcile(common.TransactionCase):

    def setUp(self):
        super(TestScenarioReconcile, self).setUp()
        tools.convert_file(self.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        self.rec_history_obj = self.env['mass.reconcile.history']
        self.mass_rec_obj = self.env['account.mass.reconcile']
        self.invoice_obj = self.env['account.invoice']
        self.bk_stmt_obj = self.env['account.bank.statement']
        self.bk_stmt_line_obj = self.env['account.bank.statement.line']
        self.acc_move_line_obj = self.env['account.move.line']
        self.mass_rec_method_obj = (
            self.env['account.mass.reconcile.method']
        )
        self.account_fx_income_id = self.ref("account.income_fx_income")
        self.account_fx_expense_id = self.ref("account.income_fx_expense")
        self.acs_model = self.env['account.config.settings']

        self.bank_journal_usd = self.env.ref('account.bank_journal_usd')

        self.currency_eur_id = self.env.ref("base.EUR").id
        company = self.env.ref('base.main_company')
        self.cr.execute(
            "UPDATE res_company SET currency_id = %s WHERE id = %s",
            [self.currency_eur_id, company.id]
        )

        self.bank_journal_usd.currency_id = self.env.ref("base.USD")

        acs_ids = self.acs_model.search(
            [('company_id', '=', company.id)]
            )

        values = {'group_multi_currency': True,
                  'currency_id': self.currency_eur_id}

        if acs_ids:
            acs_ids.write(values)
        else:
            default_vals = self.acs_model.default_get([])
            default_vals.update(values)
            acs_ids = self.acs_model.create(default_vals)

    def test_scenario_reconcile(self):
        # create invoice
        invoice = self.invoice_obj.create(
            {
                'type': 'out_invoice',
                'account_id': self.ref('account.a_recv'),
                'company_id': self.ref('base.main_company'),
                'journal_id': self.ref('account.sales_journal'),
                'partner_id': self.ref('base.res_partner_12'),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': '[PCSC234] PC Assemble SC234',
                        'account_id': self.ref('account.a_sale'),
                        'price_unit': 1000.0,
                        'quantity': 1.0,
                        'product_id': self.ref('product.product_product_3'),
                    }
                    )
                ]
            }
        )
        # validate invoice
        invoice.action_invoice_open()
        self.assertEqual('open', invoice.state)

        # create bank_statement
        statement = self.bk_stmt_obj.create(
            {
                'balance_end_real': 0.0,
                'balance_start': 0.0,
                'date': fields.Date.today(),
                'journal_id': self.ref('account.bank_journal'),
                'line_ids': [
                    (0, 0, {
                        'amount': 1000.0,
                        'partner_id': self.ref('base.res_partner_12'),
                        'name': invoice.number,
                        'ref': invoice.number,
                        }
                     )
                ]
            }
        )

        # reconcile
        line_id = None
        for l in invoice.move_id.line_ids:
            if l.account_id.id == self.ref('account.a_recv'):
                line_id = l
                break

        for statement_line in statement.line_ids:
            statement_line.process_reconciliation(
                [
                    {
                        'move_line': line_id,
                        'credit': 1000.0,
                        'debit': 0.0,
                        'name': invoice.number,
                    }
                ]
            )

        # unreconcile journal item created by previous reconciliation
        lines_to_unreconcile = self.acc_move_line_obj.search(
            [('reconciled', '=', True),
             ('statement_id', '=', statement.id)]
        )
        lines_to_unreconcile.remove_move_reconcile()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                'name': 'mass_reconcile_1',
                'account': self.ref('account.a_recv'),
                'reconcile_method': [
                    (0, 0, {
                     'name': 'mass.reconcile.simple.partner',
                     }
                     )
                ]
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual(
            'paid',
            invoice.state
        )

    def test_scenario_reconcile_currency(self):
        # create currency rate
        self.env['res.currency.rate'].create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.ref('base.USD'),
            'rate': 1.5,
        })
        # create invoice
        invoice = self.invoice_obj.create(
            {
                'type': 'out_invoice',
                'account_id': self.ref('account.a_recv'),
                'company_id': self.ref('base.main_company'),
                'currency_id': self.ref('base.USD'),
                'journal_id': self.bank_journal_usd.id,
                'partner_id': self.ref('base.res_partner_12'),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': '[PCSC234] PC Assemble SC234',
                        'account_id': self.ref('account.a_sale'),
                        'price_unit': 1000.0,
                        'quantity': 1.0,
                        'product_id': self.ref('product.product_product_3'),
                    }
                    )
                ]
            }
        )
        # validate invoice
        invoice.action_invoice_open()
        self.assertEqual('open', invoice.state)

        # create bank_statement
        statement = self.bk_stmt_obj.create(
            {
                'balance_end_real': 0.0,
                'balance_start': 0.0,
                'date': fields.Date.today(),
                'journal_id': self.bank_journal_usd.id,
                'currency_id': self.ref('base.USD'),
                'line_ids': [
                    (0, 0, {
                        'amount': 1000.0,
                        'amount_currency': 1500.0,
                        'partner_id': self.ref('base.res_partner_12'),
                        'name': invoice.number,
                        'ref': invoice.number,
                        }
                     )
                ]
            }
        )

        # reconcile
        line_id = None
        for l in invoice.move_id.line_ids:
            if l.account_id.id == self.ref('account.a_recv'):
                line_id = l
                break

        for statement_line in statement.line_ids:
            statement_line.process_reconciliation(
                [
                    {
                        'move_line': line_id,
                        'credit': 1000.0,
                        'debit': 0.0,
                        'name': invoice.number,
                    }
                ]
            )
        # unreconcile journal item created by previous reconciliation
        lines_to_unreconcile = self.acc_move_line_obj.search(
            [('reconciled', '=', True),
             ('statement_id', '=', statement.id)]
        )
        lines_to_unreconcile.remove_move_reconcile()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                'name': 'mass_reconcile_1',
                'account': self.ref('account.a_recv'),
                'reconcile_method': [
                    (0, 0, {
                     'name': 'mass.reconcile.simple.partner',
                     }
                     )
                ]
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual(
            'paid',
            invoice.state
        )
