# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.osv import expression


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    def _get_ref_fields(self):
        return ['name', 'ref']

    def _get_domain(self):
        domain = expression.OR([
            [('transaction_ref', 'ilike', self[x])]
            for x in self._get_ref_fields()
        ])
        return domain

    @api.multi
    def get_reconciliation_proposition(self, excluded_ids=None):
        """Look for transaction_ref to give them as proposition move line."""
        self.ensure_one()
        if any([self[x] for x in self._get_ref_fields()]):
            # If the transaction has no partner, look for match in payable and
            # receivable account anyway
            overlook_partner = not self.partner_id
            domain = self._get_domain()
            match_recs = self.get_move_lines_for_reconciliation(
                excluded_ids=excluded_ids, limit=2, additional_domain=domain,
                overlook_partner=overlook_partner)
            if match_recs and len(match_recs) == 1:
                return match_recs
        _super = super(AccountBankStatementLine, self)
        return _super.get_reconciliation_proposition(excluded_ids=excluded_ids)
