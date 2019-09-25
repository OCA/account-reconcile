# © 2018-19 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.osv import expression


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _domain_move_lines_for_reconciliation(
            self, st_line, aml_accounts, partner_id,
            excluded_ids=None, search_str=False):
        domain = super()._domain_move_lines_for_reconciliation(
            st_line, aml_accounts, partner_id,
            excluded_ids=excluded_ids, search_str=search_str)
        domain = expression.AND([domain, [
            ("account_id.exclude_bank_reconcile", "!=", True)]])
        return domain

    @api.model
    def _domain_move_lines_for_manual_reconciliation(
            self, account_id, partner_id=False,
            excluded_ids=None, search_str=False):
        domain = super()._domain_move_lines_for_manual_reconciliation(
            account_id, partner_id=partner_id,
            excluded_ids=excluded_ids, search_str=search_str)
        domain = expression.AND([domain, [
            ("account_id.exclude_bank_reconcile", "!=", True)]])
        return domain
