# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp import models, api, fields
from openerp.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    prepared_account_id = fields.Many2one(
        'account.account', string='Account')
    prepared_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic account')

    @api.model
    def _domain_move_lines_for_reconciliation(
            self, st_line, excluded_ids=None, str=False,
            additional_domain=None):
        if st_line.prepared_account_id:
            additional_domain = expression.AND([
                expression.normalize_domain(additional_domain)
                if additional_domain else [],
                [('account_id', '=', st_line.prepared_account_id.id)],
            ])
        if st_line.prepared_analytic_account_id:
            additional_domain = expression.AND([
                expression.normalize_domain(additional_domain)
                if additional_domain else [],
                [('analytic_account_id', '=',
                  st_line.prepared_analytic_account_id.id)],
            ])
        return super(AccountBankStatementLine, self)\
            ._domain_move_lines_for_reconciliation(
                st_line, excluded_ids=excluded_ids, str=str,
                additional_domain=additional_domain)

    @api.model
    def get_statement_line_for_reconciliation(self, st_line):
        vals = super(AccountBankStatementLine, self)\
            .get_statement_line_for_reconciliation(st_line)
        if st_line.prepared_account_id:
            vals['prepared_account_id'] = st_line.prepared_account_id.id
        if st_line.prepared_analytic_account_id:
            vals['prepared_analytic_account_id'] =\
                st_line.prepared_analytic_account_id.id
        return vals
