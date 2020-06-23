# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import models, fields, api
from odoo.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    _order = "statement_id desc, sequence, id desc"


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    # Overload Section
    @api.model
    def get_move_lines_for_bank_statement_line(
        self, st_line_id, partner_id=None,
        excluded_ids=None, search_str=False, offset=0, limit=None
    ):
        """ Returns move lines for the bank statement reconciliation widget,
            formatted as a list of dicts

            :param st_line_id: ids of the statement lines
            :param partner_id: optional partner id to select only the moves
                line corresponding to the partner
            :param excluded_ids: optional move lines ids excluded from the
                result
            :param search_str: optional search (can be the amout, display_name,
                partner name, move line name)
            :param offset: offset of the search result (to display pager)
            :param limit: number of the result to search
        """
        st_line = self.env['account.bank.statement.line'].browse(st_line_id)
        # Blue lines = payment on bank account not assigned to a statement yet
        aml_accounts = [
            st_line.journal_id.default_credit_account_id.id,
            st_line.journal_id.default_debit_account_id.id
        ]
        if partner_id is None:
            partner_id = st_line.partner_id.id
        if st_line.journal_id.reconcile_mode == 'journal_account':
            additional_domain = self.get_date_additional_domain(st_line)
            domain = self._domain_move_lines_for_reconciliation(
                st_line, aml_accounts, partner_id,
                excluded_ids=excluded_ids, search_str=search_str,
            )
            # Domain from caller
            additional_domain = expression.normalize_domain(additional_domain)
            domain = expression.AND([domain, additional_domain])
        else:
            domain = self._domain_move_lines_for_reconciliation(
                st_line, aml_accounts, partner_id,
                excluded_ids=excluded_ids, search_str=search_str
            )
        recs_count = self.env['account.move.line'].search_count(domain)
        aml_recs = self.env['account.move.line'].search(
            domain, offset=offset,
            limit=limit,
            order="date_maturity desc, id desc"
        )
        target_currency = st_line.currency_id or\
            st_line.journal_id.currency_id or\
            st_line.journal_id.company_id.currency_id
        journal_ids = st_line.journal_id.ids
        return self.with_context(journal_ids=journal_ids)._prepare_move_lines(
            aml_recs,
            target_currency=target_currency,
            target_date=st_line.date,
            recs_count=recs_count
        )

    @api.model
    def _get_move_line_reconciliation_proposition(
            self, account_id, partner_id=None
    ):
        """ Returns two lines whose amount are opposite """
        Account_move_line = self.env['account.move.line']
        ir_rules_query = Account_move_line._where_calc([])
        Account_move_line._apply_ir_rules(ir_rules_query, 'read')
        from_clause, where_clause, where_clause_params = ir_rules_query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or ''

        # Get pairs
        query = """
            SELECT a.id, b.id
            FROM account_move_line a, account_move_line b,
                 account_move move_a, account_move move_b,
                 account_journal journal_a, account_journal journal_b
            WHERE a.id != b.id
            AND move_a.id = a.move_id
            AND (move_a.state = 'posted'
            OR (move_a.state = 'draft' AND journal_a.post_at_bank_rec))
            AND move_a.journal_id = journal_a.id
            AND move_b.id = b.move_id
            AND move_b.journal_id = journal_b.id
            AND (move_b.state = 'posted'
            OR (move_b.state = 'draft' AND journal_b.post_at_bank_rec))
            AND a.amount_residual = -b.amount_residual
            AND NOT a.reconciled
            AND a.account_id = %s
            AND (%s IS NULL AND b.account_id = %s)
            AND (%s IS NULL AND NOT b.reconciled OR b.id = %s)
            AND (%s is NULL OR (a.partner_id = %s AND b.partner_id = %s))
            AND a.id IN (SELECT id FROM {0})
            AND b.id IN (SELECT id FROM {0})
            ORDER BY a.date desc
            LIMIT 1
            """.format(from_clause + where_str)
        move_line_id = self.env.context.get('move_line_id') or None
        params = [
            account_id,
            move_line_id, account_id,
            move_line_id, move_line_id,
            partner_id, partner_id, partner_id,
        ] + where_clause_params + where_clause_params
        self.env.cr.execute(query, params)
        pairs = self.env.cr.fetchall()

        if pairs:
            return Account_move_line.browse(pairs[0])
        return Account_move_line

    @api.model
    def _domain_move_lines_for_reconciliation(
        self, st_line, aml_accounts, partner_id,
        excluded_ids=None, search_str=False
    ):
        """ Return the domain for account.move.line records
            which can be used for bank statement reconciliation.

            :param aml_accounts:
            :param partner_id:
            :param excluded_ids:
            :param search_str:
        """
        domain = super(AccountReconciliation, self)._domain_move_lines_for_reconciliation(
            st_line, aml_accounts, partner_id,
            excluded_ids=excluded_ids, search_str=search_str)
        if st_line.journal_id.reconcile_mode == 'journal_account':
            bank_reconcile_account_allowed_ids = \
                st_line.journal_id.bank_reconcile_account_allowed_ids.ids
            args = [
                ('statement_line_id', '=', False),
                ('reconciled', '=', False),
                ('account_id.reconcile', '=', True),
            ]
            if bank_reconcile_account_allowed_ids:
                reconciliation_account_all = aml_accounts + \
                    bank_reconcile_account_allowed_ids
                args += [
                    ('account_id', 'in', reconciliation_account_all),
                ]
            domain = expression.AND([domain, args])
        return domain

    @api.multi
    def get_date_additional_domain(self, st_line):
        date_string = fields.Date.from_string(st_line.date)
        search_limit_days = st_line.statement_id and \
            st_line.statement_id.journal_id and \
            st_line.statement_id.journal_id.search_limit_days or 0.0
        if date_string and search_limit_days:
            limit_days_after = date_string + timedelta(
                days=search_limit_days)
            limit_days_before = date_string - timedelta(
                days=search_limit_days)
            domain = [('date', '<', limit_days_after),
                      ('date', '>', limit_days_before)]
            return domain
        else:
            return []

    @api.model
    def get_bank_statement_line_data(self, st_line_ids, excluded_ids=None):
        """Merge from account_bank_reconciliation_rule module
            Returns the data required to display a reconciliation widget, for
            each statement line in self

            :param st_line_id: ids of the statement lines
            :param excluded_ids: optional move lines ids excluded from the
                result
        """
        excluded_ids = excluded_ids or []

        # Make a search to preserve the table's order.
        bank_statement_lines = self.env['account.bank.statement.line'].search(
            [('id', 'in', st_line_ids)]
        )
        reconcile_model = self.env['account.reconcile.model'].search(
            [('rule_type', '!=', 'writeoff_button')]
        )

        # Search for missing partners when opening the reconciliation widget.
        partner_map = self._get_bank_statement_line_partners(
            bank_statement_lines)

        matching_amls = reconcile_model._apply_rules(
            bank_statement_lines,
            excluded_ids=excluded_ids,
            partner_map=partner_map
        )

        results = {
            'lines': [],
            'value_min': 0,
            'value_max': len(bank_statement_lines),
            'reconciled_aml_ids': [],
        }

        # Iterate on st_lines to keep the same order in the results list.
        bank_statements_left = self.env['account.bank.statement']
        for line in bank_statement_lines:
            if matching_amls[line.id].get('status') == 'reconciled':
                reconciled_move_lines = \
                    matching_amls[line.id].get('reconciled_lines')
                results['value_min'] += 1
                results['reconciled_aml_ids'] += \
                    reconciled_move_lines and reconciled_move_lines.ids or []
            else:
                aml_ids = matching_amls[line.id]['aml_ids']
                bank_statements_left += line.statement_id
                target_currency = line.currency_id or\
                    line.journal_id.currency_id or\
                    line.journal_id.company_id.currency_id

                amls = aml_ids and self.env['account.move.line'].browse(
                    aml_ids)
                journal_ids = [line.journal_id.id]
                line_vals = {
                    'st_line': self._get_statement_line(line),
                    'reconciliation_proposition':
                        aml_ids and
                        self.with_context(
                            journal_ids=journal_ids
                        )._prepare_move_lines(
                            amls, target_currency=target_currency,
                            target_date=line.date
                        ) or [],
                    'model_id': matching_amls[line.id].get('model') and
                        matching_amls[line.id]['model'].id,
                    'write_off':
                        matching_amls[line.id].get('status') == 'write_off',
                }
                if (line.journal_id.set_default_reconcile_partner and
                     not line.partner_id and
                     partner_map.get(line.id)
                ):
                    partner_obj = self.env['res.partner']
                    partner = partner_obj.browse(partner_map[line.id])
                    line_vals.update({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                    })
                results['lines'].append(line_vals)

        return results

    @api.model
    def _prepare_move_lines(
            self, move_lines,
            target_currency=False,
            target_date=False, recs_count=0
    ):
        """ Merge from account_bank_reconciliation_rule module
            Returns move lines formatted for the manual/bank
            reconciliation widget

            :param move_line_ids:
            :param target_currency: currency (browse) you want
            the move line debit/credit converted into
            :param target_date: date to use for the monetary conversion
        """
        ret = super(AccountReconciliation, self)._prepare_move_lines(
            move_lines, target_currency, target_date, recs_count
        )
        journal_ids = self.env.context.get('journal_ids', [])
        journals = self.env['account.journal'].browse(journal_ids)
        debit_account = journals.mapped('default_debit_account_id')
        list_account_code = debit_account.mapped('code')
        for ret_line in ret:
            if ret_line['account_code'] in list_account_code:
                ret_line.update({
                    'already_paid': True})
            else:
                ret_line.update({
                    'already_paid': False})
        return ret
