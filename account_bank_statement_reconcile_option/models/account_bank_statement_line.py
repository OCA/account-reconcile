# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import models, fields, api
from odoo.osv import expression


class AccountBankStatementLine(models.AbstractModel):
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
        domain = False
        if st_line.journal_id.reconcile_mode == 'journal_account':
            additional_domain = self.get_date_additional_domain(st_line)
            domain = self._domain_move_lines_for_reconciliation(
                st_line, aml_accounts, partner_id,
                excluded_ids=excluded_ids, search_str=search_str,
                additional_domain=additional_domain
            )
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
        return self._prepare_move_lines(
            aml_recs,
            target_currency=target_currency,
            target_date=st_line.date,
            recs_count=recs_count
        )

    @api.model
    def _get_move_line_reconciliation_proposition(self, account_id, partner_id=None):
        """ Returns two lines whose amount are opposite """
        Account_move_line = self.env['account.move.line']
        search_limit_days = self.journal_id.search_limit_days or 0
        date_line = fields.Date.from_string(self.date)
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
        if date_line and search_limit_days:
            limit_days_after = date_line + timedelta(
                days=search_limit_days)
            limit_days_before = date_line - timedelta(
                days=search_limit_days)
            params.extend([limit_days_after, limit_days_before])
            query += """AND a.date_maturity < %(limit_days_after)s \
                        AND a.date_maturity > %(limit_days_before)s
                        AND b.date_maturity < %(limit_days_after)s \
                        AND b.date_maturity > %(limit_days_before)s"""
        self.env.cr.execute(query, params)
        pairs = self.env.cr.fetchall()

        if pairs:
            return Account_move_line.browse(pairs[0])
        return Account_move_line

    @api.model
    def _domain_move_lines_for_reconciliation(
        self, st_line, aml_accounts, partner_id,
        excluded_ids=None, search_str=False, additional_domain=None
    ):
        """ Return the domain for account.move.line records
            which can be used for bank statement reconciliation.

            :param aml_accounts:
            :param partner_id:
            :param excluded_ids:
            :param search_str:
        """
        bank_reconcile_account_allowed_ids =\
            st_line.journal_id.bank_reconcile_account_allowed_ids.ids or []
        reconciliation_account_all = aml_accounts + \
            bank_reconcile_account_allowed_ids

        domain_reconciliation = [
            '&', '&',
            ('statement_line_id', '=', False),
            ('account_id', 'in', reconciliation_account_all),
            ('balance', '!=', 0.0),
        ]

        # default domain matching
        domain_matching = [
            '&', '&',
            ('reconciled', '=', False),
            ('account_id.reconcile', '=', True),
            ('balance', '!=', 0.0),
        ]

        domain = expression.OR([domain_reconciliation, domain_matching])
        if partner_id:
            domain = expression.AND([domain, [('partner_id', '=', partner_id)]])

        # Domain factorized for all reconciliation use cases
        if search_str:
            str_domain = self._domain_move_lines(search_str=search_str)
            str_domain = expression.OR([
                str_domain,
                [('partner_id.name', 'ilike', search_str)]
            ])
            domain = expression.AND([
                domain,
                str_domain
            ])

        if excluded_ids:
            domain = expression.AND([
                [('id', 'not in', excluded_ids)],
                domain
            ])
        # filter on account.move.line having the same company as the statement line
        domain = expression.AND([domain, [('company_id', '=', st_line.company_id.id)]])
        if st_line.company_id.account_bank_reconciliation_start:
            domain = expression.AND(
                [domain,
                    [('date', '>=',
                        st_line.company_id.account_bank_reconciliation_start)]]
            )
        # Domain from caller
        if additional_domain is None:
            additional_domain = []
        else:
            additional_domain = expression.normalize_domain(additional_domain)
        domain = expression.AND([domain, additional_domain])
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
