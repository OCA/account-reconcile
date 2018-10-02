# © 20118 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def get_move_lines_for_reconciliation(
            self, partner_id=None, excluded_ids=None, str=False, offset=0,
            limit=None, additional_domain=None, overlook_partner=False):
        am_lines = super(AccountBankStatementLine, self).\
            get_move_lines_for_reconciliation(
            partner_id=partner_id, excluded_ids=excluded_ids, str=str,
            offset=offset, limit=limit, additional_domain=additional_domain,
            overlook_partner=overlook_partner)
        return am_lines.filtered(
            lambda line: not line.account_id.exclude_bank_reconcile)
