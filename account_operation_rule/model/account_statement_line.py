# -*- coding: utf-8 -*-
# Author: Guewen Baconnier
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def currency_for_rules(self):
        return self.currency_id or self.statement_id.currency_id
