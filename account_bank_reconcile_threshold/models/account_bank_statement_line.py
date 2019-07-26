# -*- coding: utf-8 -*-
# Copyright 2018 Odoo SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models
from odoo.osv import expression


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    def _get_domain_reconciliation(self):
        domain = super(
            AccountBankStatementLine, self)._get_domain_reconciliation()
        if not self.company_id.account_bank_reconciliation_start:
            return domain
        domain = expression.AND([domain, [
            ('date', '>=', self.company_id.account_bank_reconciliation_start)]])
        return domain
