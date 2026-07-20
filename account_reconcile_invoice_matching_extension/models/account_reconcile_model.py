from odoo import models, fields, api
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from dateutil.relativedelta import relativedelta
from decimal import Decimal


class AccountReconcileModel(models.Model):

    _inherit = 'account.reconcile.model'

    invoice_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Term',
        help="if set, this payment term will be used to match invoices for reconciliation with bank statement lines, instead of the payment term defined on the invoice. This can be used to set the automatical reconciliation for skonto payment."
    )
    match_total_amount_exact = fields.Boolean(
        string='Match Total Amount (Exactly)',
        default=False,
        help='If set, the reconciliation propositions will only be accepted if the total residual amount of the candidate move lines is exactly equal to the given percent of statement line amount.'
    )

    def _get_invoice_matching_query(self, st_lines_with_partner, excluded_ids):
        query, params = super()._get_invoice_matching_query(st_lines_with_partner, excluded_ids)
        # (changes) add move_invoice_date and match with payment term
        query = query.replace("AS aml_amount_residual_currency,", "AS aml_amount_residual_currency, move.invoice_date AS move_invoice_date, ")
        if self.invoice_payment_term_id and self.rule_type == 'invoice_matching':
            query = query.split("WHERE")[0] + "WHERE move.invoice_payment_term_id = %(invoice_payment_term_id)s AND" + query.split("WHERE")[1]
            params['invoice_payment_term_id'] = self.invoice_payment_term_id.id
        return query, params


    def _check_rule_propositions(self, statement_line, candidates):
        ''' match total amount exactly'''

        def _decimal_places(n: float) -> int:
            d = Decimal(str(n))
            return abs(d.as_tuple().exponent)

        if not self.match_total_amount:
            return True

        if self.invoice_payment_term_id and self.invoice_payment_term_id.discount_delay:
            discount_date = statement_line.date - relativedelta(days=self.invoice_payment_term_id.discount_delay)
            candidates = [aml for aml in candidates if aml['move_invoice_date'] and aml['move_invoice_date'] >= discount_date]

        if not candidates:
            return False

        #from pudb.remote import set_trace; set_trace(term_size=(160, 60), host='0.0.0.0', port=1984)
        if self.match_total_amount_exact:
            reconciliation_overview, open_balance_vals = statement_line._prepare_reconciliation([{
                'currency_id': aml['aml_currency_id'],
                'amount_residual': aml['aml_amount_residual'],
                'amount_residual_currency': aml['aml_amount_residual_currency'],
            } for aml in candidates])
                
            # Match total residual amount.
            line_currency = statement_line.foreign_currency_id or statement_line.currency_id
            line_residual = statement_line.amount_residual
            line_residual_after_reconciliation = line_residual
                        
            for reconciliation_vals in reconciliation_overview:
                line_vals = reconciliation_vals['line_vals']
                if line_vals['currency_id']:
                    line_residual_after_reconciliation -= line_vals['amount_currency']
                else:   
                    line_residual_after_reconciliation -= line_vals['debit'] - line_vals['credit']
                    
            # Statement line amount is equal to the total residual.
            if line_currency.is_zero(line_residual_after_reconciliation):
                return True 
            residual_difference = line_residual - line_residual_after_reconciliation
            reconciled_percentage = 100 - abs(line_residual_after_reconciliation) / abs(residual_difference) * 100 if (residual_difference != 0) else 0
            pd = _decimal_places(self.match_total_amount_param)
            return float_compare(reconciled_percentage, self.match_total_amount_param, precision_digits=pd) == 0

        return super()._check_rule_propositions(statement_line, candidates)
