# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def auto_reconcile(self):
        # If we don't have esr_reconcile we want the default odoo way
        if not self.env.context.get('struct_reconcile'):
            return super(AccountBankStatementLine, self).auto_reconcile()
        # otherwise use struct reconcile
        else:
            return self.auto_reconcile_struct()

    @api.multi
    def auto_reconcile_struct(self):
        """ Reconcile the Bank statement line and acount move line
        based on only the strctured reference

        """
        self.ensure_one()
        match_recs = self.env['account.move.line']
        company_currency = self.journal_id.company_id.currency_id
        # customized: dropped unneeded params
        precision = company_currency.decimal_places
        params = {
            'company_id': self.env.user.company_id.id,
            'account_payable_receivable': (
                self.journal_id.default_credit_account_id.id,
                self.journal_id.default_debit_account_id.id
            ),
            'partner_id': self.partner_id.id,
            'ref': self.name.strip(),
            'amount': self.amount,
            'precision': precision
        }
        # Try to get Structured Ref match
        if self.name:
            sql_query = self._get_sql_query()
            self.env.cr.execute(sql_query, params)
            match_recs = self.env.cr.dictfetchall()
            if len(match_recs) > 1:
                return False
        # Customizations done. odoo code from here on.
        if not match_recs:
            return False

        match_recs = self.env['account.move.line'].browse(
            [aml.get('id') for aml in match_recs]
        )
        # Now reconcile
        counterpart_aml_dicts = []
        payment_aml_rec = self.env['account.move.line']
        for aml in match_recs:
            if aml.account_id.internal_type == 'liquidity':
                payment_aml_rec = (payment_aml_rec | aml)
            else:
                amount = aml.currency_id and aml.amount_residual_currency \
                    or aml.amount_residual
                counterpart_aml_dicts.append({
                    'name': aml.name if aml.name != '/' else aml.move_id.name,
                    'debit': amount < 0 and -amount or 0,
                    'credit': amount > 0 and amount or 0,
                    'move_line': aml
                })

        try:
            with self._cr.savepoint():
                counterpart = self.process_reconciliation(
                    counterpart_aml_dicts=counterpart_aml_dicts,
                    payment_aml_rec=payment_aml_rec
                )
            return counterpart
        except UserError:
            # A configuration / business logic error that makes it impossible
            # to auto-reconcile should not be raised
            # since automatic reconciliation is just an amenity and the user
            # will get the same exception when manually
            # reconciling. Other types of exception are (hopefully)
            # programmation errors and should cause a stacktrace.
            self.invalidate_cache()
            self.env['account.move'].invalidate_cache()
            self.env['account.move.line'].invalidate_cache()
            return False

    def _get_common_sql_query_ignore_partner(self):
        """ Selects the account move lines based on account type and company.

        Basequery, returns all lines matching filter clause needs to be added.
        """
        acc_type = "acc.internal_type IN ('payable', 'receivable')" if (
            self.partner_id or False
        ) else "acc.reconcile = true"
        account_clause = ''
        if self.journal_id.default_credit_account_id and \
                self.journal_id.default_debit_account_id:
            account_clause = "(aml.statement_id IS NULL AND aml.account_id IN \
            %(account_payable_receivable)s AND aml.payment_id IS NOT NULL) OR"
        query = """
        SELECT aml.id
        FROM account_move_line aml
        JOIN account_account acc ON acc.id = aml.account_id
        WHERE aml.company_id = %(company_id)s
        AND ({0} ( {1} AND aml.reconciled = false))
        """
        return query.format(account_clause, acc_type)

    def _get_sql_query(self):
        sql_query = self._get_common_sql_query_ignore_partner() + \
            " AND POSITION(aml.ref in %(ref)s) > 0" \
            " AND aml.ref is not null" \
            " AND round(aml.amount_residual,%(precision)s)" \
            " = round(%(amount)s,%(precision)s) " \
            " ORDER BY" \
            " date_maturity asc, aml.id asc"
        return sql_query
