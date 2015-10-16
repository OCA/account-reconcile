# -*- coding: utf-8 -*-
# © 2016 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.multi
    def get_reconciliation_proposition(self, excluded_ids=None):
        """ Look for transaction_ref to give them as proposition move line """
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
