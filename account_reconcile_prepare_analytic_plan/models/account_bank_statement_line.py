# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, api, fields
from openerp.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    prepared_analytic_plan_instance_id = fields.Many2one(
        'account.analytic.plan.instance', string='Analytic plan')

    @api.model
    def _domain_move_lines_for_reconciliation(
            self, st_line, excluded_ids=None, str=False,
            additional_domain=None):
        if st_line.prepared_analytic_plan_instance_id:
            additional_domain = expression.AND([
                expression.normalize_domain(additional_domain)
                if additional_domain else [],
                [('analytics_id', '=',
                  st_line.prepared_analytic_plan_instance_id.id)],
            ])
        return super(AccountBankStatementLine, self)\
            ._domain_move_lines_for_reconciliation(
                st_line, excluded_ids=excluded_ids, str=str,
                additional_domain=additional_domain)

    @api.model
    def get_statement_line_for_reconciliation(self, st_line):
        vals = super(AccountBankStatementLine, self)\
            .get_statement_line_for_reconciliation(st_line)
        if st_line.prepared_analytic_plan_instance_id:
            vals['prepared_analytic_plan_instance_id'] =\
                st_line.prepared_analytic_plan_instance_id.id
        return vals
