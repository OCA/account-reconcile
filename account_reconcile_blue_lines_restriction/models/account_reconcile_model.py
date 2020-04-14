# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class AccountReconcileModel(models.Model):

    _inherit = 'account.reconcile.model'

    @api.multi
    def _apply_conditions(self, query, params):
        """Remove AMLs with account not allowed for reconciliation from
           blue lines appearance conditions"""
        new_query, new_params = super()._apply_conditions(query, params)
        if self.rule_type == 'invoice_matching':
            new_query += '''
                AND (
                    -- modified blue lines appearance conditions
                    aml.account_id IN (
                        journal.default_credit_account_id,
                        journal.default_debit_account_id
                    )
                    AND aml.statement_id IS NULL
                    AND (
                        company.account_bank_reconciliation_start IS NULL
                        OR
                        aml.date > company.account_bank_reconciliation_start
                    )
                    -- This line restricts propositions to lines on
                    -- accounts allowing reconciliation
                    AND account.reconcile IS TRUE
                    OR (
                        -- black lines appearance conditions
                        account.reconcile IS TRUE
                        AND aml.reconciled IS FALSE
                    )
                )
            '''
        return new_query, new_params
