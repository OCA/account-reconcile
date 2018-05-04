# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_statement_partner_lines,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_statement_partner_lines is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_statement_partner_lines is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_statement_partner_lines.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def prepare_aml_for_reconciliation_from_ids(self,
                                                target_currency_id=False,
                                                target_date=False):
        currency_obj = self.env['res.currency']
        target_currency = currency_obj.browse([target_currency_id])[0]
        return self\
            .prepare_move_lines_for_reconciliation_widget(self,
                                                          target_currency,
                                                          target_date)
