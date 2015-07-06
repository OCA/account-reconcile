# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
import time


class testScenarioReconcile(common.TransactionCase):

    def setUp(self):
        super(testScenarioReconcile, self).setUp()
        self.rec_history_obj = self.registry('easy.reconcile.history')
        self.easy_rec_obj = self.registry('account.easy.reconcile')
        self.invoice_obj = self.registry('account.invoice')
        self.bk_stmt_obj = self.registry('account.bank.statement')
        self.bk_stmt_line_obj = self.registry('account.bank.statement.line')
        self.acc_move_line_obj = self.registry('account.move.line')
        self.easy_rec_method_obj = (
            self.registry('account.easy.reconcile.method')
        )

    def test_scenario_reconcile(self):
        # create invoice
        inv_id = self.invoice_obj.create(
            self.cr,
            self.uid,
            {
                'type': 'out_invoice',
                'account_id': self.ref('account.a_recv'),
                'company_id': self.ref('base.main_company'),
                'currency_id': self.ref('base.CHF'),
                'journal_id': self.ref('account.bank_journal'),
                'partner_id': self.ref('base.res_partner_12'),
                'invoice_line': [
                    (0, 0, {
                        'name': '[PCSC234] PC Assemble SC234',
                        'price_unit': 1000.0,
                        'quantity': 1.0,
                        'product_id': self.ref('product.product_product_3'),
                        'uos_id': self.ref('product.product_uom_unit'),
                    }
                    )
                ]
            }
        )
        # validate invoice
        self.invoice_obj.signal_workflow(
            self.cr,
            self.uid,
            [inv_id],
            'invoice_open'
        )
        invoice_record = self.invoice_obj.browse(self.cr, self.uid, [inv_id])
        self.assertEqual('open', invoice_record.state)

        # create bank_statement
        bk_stmt_id = self.bk_stmt_obj.create(
            self.cr,
            self.uid,
            {
                'balance_end_real': 0.0,
                'balance_start': 0.0,
                'date': time.strftime('%Y-%m-%d'),
                'journal_id': self.ref('account.bank_journal'),
                'line_ids': [
                    (0, 0, {
                        'amount': 1000.0,
                        'partner_id': self.ref('base.res_partner_12'),
                        'name': 'EXT001'
                        }
                     )
                ]
            }
        )

        # reconcile
        line_id = None
        for l in invoice_record.move_id.line_id:
            if l.account_id.id == self.ref('account.a_recv'):
                line_id = l
                break

        statement = self.bk_stmt_obj.browse(self.cr, self.uid, bk_stmt_id)
        for statement_line in statement.line_ids:
            self.bk_stmt_line_obj.process_reconciliation(
                self.cr, self.uid, statement_line.id,
                [
                    {
                        'counterpart_move_line_id': line_id.id,
                        'credit': 1000.0,
                        'debit': 0.0,
                        'name': line_id.name
                    }
                ]
            )

        # unreconcile journal item created by previous reconciliation
        lines_to_unreconcile = self.acc_move_line_obj.search(
            self.cr,
            self.uid,
            [('reconcile_ref', '!=', False),
             ('statement_id', '=', bk_stmt_id)]
        )
        self.acc_move_line_obj._remove_move_reconcile(
            self.cr,
            self.uid,
            lines_to_unreconcile
        )

        # create the easy reconcile record
        easy_rec_id = self.easy_rec_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'easy_reconcile_1',
                'account': self.ref('account.a_recv'),
                'reconcile_method': [
                    (0, 0, {
                     'name': 'easy.reconcile.simple.partner',
                     }
                     )
                ]
            }
        )

        # call the automatic reconcilation method
        self.easy_rec_obj.run_reconcile(
            self.cr,
            self.uid,
            [easy_rec_id]
        )
        self.assertEqual(
            'paid',
            self.invoice_obj.browse(self.cr, self.uid, inv_id).state
        )
