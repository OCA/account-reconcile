"""Unit test to check wether period taken from transaction date."""
##############################################################################
#
#    Copyright (C) 2015 Therp BV - http://therp.nl.
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
        # Setup dates for testing:
        current_year = time.strftime('%Y')
        invoice_date = '%s-07-01' % current_year  # July
        statement_date = '%s-09-01' % current_year  # September
        transaction_date = '%s-08-01' % current_year  # August
        # Get references to demo data
        partner_agrolait = self.env.ref('base.res_partner_2')
        account_rcv = self.env.ref('account.a_recv')
        currency_usd = self.env.ref('base.USD')
        bank_journal_usd = self.env.ref('account.bank_journal_usd')
        # Get other models from registry:
        account_invoice_model = self.env['account.invoice']
        statement_line_model = self.env['account.bank.statement.line']
        # Create invoice in dollars:
        invoice = account_invoice_model.create({
            'partner_id': partner_agrolait.id,
            'currency_id': currency_usd.id,
            'reference_type': 'none',
            'name': 'invoice to client',
            'account_id': account_rcv.id,
            'type': 'out_invoice',
            'date_invoice': invoice_date,
        })
        self.env['account.invoice.line'].create({
            'name': 'product that cost 100.00',
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
        })
        # Validate sale:
        invoice.signal_workflow('invoice_open')
        # Bank statement from September:
        bank_stmt = self.env['account.bank.statement'].create({
            'journal_id': bank_journal_usd.id,
            'date': statement_date,
        })
        # Transaction from August:
        bank_stmt_line = statement_line_model.create({
            'name': 'complete payment',
            'statement_id': bank_stmt.id,
            'partner_id': partner_agrolait.id,
            'amount': 100.00,
            'date': transaction_date,
        })
        # Reconcile the payment with the invoice:
        for l in invoice.move_id.line_id:
            if l.account_id == account_rcv:
                line = l
                break
        statement_line_model.process_reconciliation(
            bank_stmt_line.id, [{
                'counterpart_move_line_id': line.id,
                'credit': 100.0,
                'debit': 0.0,
                'name': line.name,
            }])
        # Get period for transaction date:
        test_period = self.env['account.period'].find(dt=transaction_date)[0]
        # Period in move line for bank transaction, and for move should equal
        # period from transaction:
        for move_line in bank_stmt.move_line_ids:
            self.assertEquals(
                move_line.period_id, test_period)
            self.assertEquals(
                move_line.move_id.period_id, test_period)
