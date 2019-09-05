# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models
from odoo.osv import expression


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _get_final_domain(self, domain):
        final_domain = expression.AND(
            [domain, [('account_id.exclude_from_bank_statement_reconciliation',
                       '=', False)]])
        return final_domain
