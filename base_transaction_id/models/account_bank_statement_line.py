# Copyright 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import float_round, float_repr
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def get_reconciliation_proposition(self, excluded_ids=None):
        """Look for transaction_ref to give them as proposition move line."""
        self.ensure_one()
        if self.name:
            # If the transaction has no partner, look for match in payable and
            # receivable account anyway
            overlook_partner = not self.partner_id
            domain = [('transaction_ref', 'ilike', self.name)]
            match_recs = self.get_move_lines_for_reconciliation(
                excluded_ids=excluded_ids, limit=2, additional_domain=domain,
                overlook_partner=overlook_partner)
            if match_recs and len(match_recs) == 1:
                return match_recs
        _super = super(AccountBankStatementLine, self)
        return _super.get_reconciliation_proposition(excluded_ids=excluded_ids)

    @api.multi
    def auto_reconcile(self):
        """ Extend super method. If no matches found, try with transaction_ref
            instead of ref """
        self.ensure_one()
        _super = super(AccountBankStatementLine, self)
        res = _super.auto_reconcile()
        if res:
            return res
        match_recs = self.env['account.move.line']
        amount = self.amount_currency or self.amount
        company_currency = self.journal_id.company_id.currency_id
        st_line_currency = self.currency_id or self.journal_id.currency_id
        currency = (st_line_currency and st_line_currency !=
                    company_currency) and st_line_currency.id or False
        precision = st_line_currency and st_line_currency.decimal_places or \
            company_currency.decimal_places
        params = {'company_id': self.env.user.company_id.id,
                  'account_payable_receivable': (
                      self.journal_id.default_credit_account_id.id,
                      self.journal_id.default_debit_account_id.id
                  ),
                  'amount': float_repr(float_round(amount,
                                                   precision_digits=precision),
                                       precision_digits=precision),
                  'partner_id': self.partner_id.id,
                  'ref': self.ref or self.name,
                  }
        field = currency and 'amount_residual_currency' or 'amount_residual'
        liquidity_field = currency and 'amount_currency' or amount > 0 and \
            'debit' or 'credit'
        # Look for structured communication match using transaction_ref
        if self.name:
            sql_query = self._get_common_sql_query() +  \
                " AND aml.transaction_ref = %(ref)s AND (" + field + \
                " = %(amount)s OR (acc.internal_type='liquidity' AND " + \
                liquidity_field + " = %(amount)s)) " \
                "ORDER BY date_maturity asc, aml.id asc"
            self.env.cr.execute(sql_query, params)
            match_recs = self.env.cr.dictfetchall()
            if len(match_recs) > 1:
                return False
        if not match_recs:
            return False
        match_recs = self.env['account.move.line'].browse(
            [aml.get('id') for aml in match_recs])
        # Now reconcile
        counterpart_aml_dicts = []
        payment_aml_rec = self.env['account.move.line']
        for aml in match_recs:
            if aml.account_id.internal_type == 'liquidity':
                payment_aml_rec = (payment_aml_rec | aml)
            else:
                amount = aml.currency_id and aml.amount_residual_currency or \
                    aml.amount_residual
                counterpart_aml_dicts.append({
                    'name': aml.name if aml.name != '/' else aml.move_id.name,
                    'debit': amount < 0 and -amount or 0,
                    'credit': amount > 0 and amount or 0,
                    'move_line': aml})
        try:
            with self._cr.savepoint():
                counterpart = self.process_reconciliation(
                    counterpart_aml_dicts=counterpart_aml_dicts,
                    payment_aml_rec=payment_aml_rec)
            return counterpart
        except UserError:
            # A configuration / business logic error that makes it impossible
            # to auto-reconcile should not be raised
            # since automatic reconciliation is just an amenity and the user
            # will get the same exception when manually
            # reconciling. Other types of exception are (hopefully)
            # programmatic errors and should cause a stacktrace.
            self.invalidate_cache()
            self.env['account.move'].invalidate_cache()
            self.env['account.move.line'].invalidate_cache()
            return False
