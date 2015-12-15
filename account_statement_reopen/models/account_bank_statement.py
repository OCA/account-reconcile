# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def button_reopen(self):
        self.write({'state': 'draft'})
