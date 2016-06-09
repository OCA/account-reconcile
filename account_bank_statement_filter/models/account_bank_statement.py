# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    def _domain_move_lines_for_reconciliation(
            self, st_line, excluded_ids=None, str=False,
            additional_domain=None):
        res = super(
            AccountBankStatementLine,
            self)._domain_move_lines_for_reconciliation(
            st_line, excluded_ids=excluded_ids, str=str,
            additional_domain=additional_domain)
        if str and str != '/':
            res.insert(-1, '|', )
            res.append(('account_id.code', 'ilike', str))
        return res
