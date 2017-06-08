"""Unit test to check wether period taken from transaction date."""
##############################################################################
#
#    Copyright (C) 2015 Therp BV - http://therp.nl.
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tests.common import TransactionCase
import time


class TestReconciliation(TransactionCase):
    """Tests to make sure that transactions take period from statement line."""

    def test_period_from_transaction(self):
        """Move line for reconciliation should take period from transaction.

        Setup a bank statement and a bank statement line (transaction) with
        dates from different period. Created moves produced by reconciliation
        should take the period from the line date, not from the statement date.
        """
        cr, uid = self.cr, self.uid
        # Setup dates for testing:
        current_year = time.strftime('%Y')
        invoice_date = '%s-07-01' % current_year  # july
        statement_date = '%s-09-01' % current_year  # september
        transaction_date = '%s-08-01' % current_year  # august
        # Get references to demo data
        data_model = self.registry('ir.model.data')
        partner_agrolait_id = data_model.get_object_reference(
            cr, uid, 'base', 'res_partner_2')[1]
        account_rcv_id = data_model.get_object_reference(
            cr, uid, 'account', 'a_recv')[1]
        currency_usd_id = data_model.get_object_reference(
            cr, uid, 'base', 'USD')[1]
        bank_journal_usd_id = data_model.get_object_reference(
            cr, uid, 'account', 'bank_journal_usd')[1]
        account_usd_id = data_model.get_object_reference(
            cr, uid, 'account', 'usd_bnk')[1]
        # Get other models from registry:
        period_model = self.registry('account.period')
        account_invoice_model = self.registry('account.invoice')
        account_invoice_line_model = self.registry('account.invoice.line')
        statement_model = self.registry('account.bank.statement')
        statement_line_model = self.registry('account.bank.statement.line')
        # Create invoice in dollars:
        invoice_id = account_invoice_model.create(
            cr, uid, {
                'partner_id': partner_agrolait_id,
                'currency_id': currency_usd_id,
                'reference_type': 'none',
                'name': 'invoice to client',
                'account_id': account_rcv_id,
                'type': 'out_invoice',
                'date_invoice': invoice_date,
            }
        )
        account_invoice_line_model.create(
            cr, uid, {
                'name': 'product that cost 100.00',
                'quantity': 1.0,
                'price_unit': 100.0,
                'invoice_id': invoice_id,
            }
        )
        # Validate sale:
        account_invoice_model.signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = account_invoice_model.browse(cr, uid, [invoice_id])
        # Bank statement from september:
        bank_stmt_id = statement_model.create(
            cr, uid, {
                'journal_id': bank_journal_usd_id,
                'date': statement_date,
            }
        )
        # Transaction from august:
        bank_stmt_line_id = statement_line_model.create(
            cr, uid, {
                'name': 'complete payment',
                'statement_id': bank_stmt_id,
                'partner_id': partner_agrolait_id,
                'amount': 100.00,
                'date': transaction_date,
            }
        )
        # Reconcile the payment with the invoice:
        for l in invoice_record.move_id.line_id:
            if l.account_id.id == account_rcv_id:
                line_id = l
                break
        statement_line_model.process_reconciliation(
            cr, uid, bank_stmt_line_id, [{
                'counterpart_move_line_id': line_id.id,
                'credit': 100.0,
                'debit': 0.0,
                'name': line_id.name,
            }]
        )
        # Get period for transaction date:
        test_period_id = period_model.find(cr, uid, dt=transaction_date)[0]
        # Get move lines for bank statement:
        move_line_ids = statement_model.browse(
            cr, uid, bank_stmt_id).move_line_ids
        # Period in move line for bank transaction, and for move should equal
        # period from transaction:
        for move_line in move_line_ids:
            if move_line.account_id.id == account_usd_id:
                self.assertEquals(
                    move_line.period_id.id, test_period_id)
                self.assertEquals(
                    move_line.move_id.period_id.id, test_period_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
