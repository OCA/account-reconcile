# -*- coding: utf-8 -*-
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from openerp import models, fields, api
from openerp.osv import expression


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    transaction_ref = fields.Char(
        'Transaction Ref.',
        index=True,
        copy=False
    )

    @api.multi
    def prepare_move_lines_for_reconciliation_widget(self,
                                                     target_currency=False,
                                                     target_date=False):
        prepared_lines = []
        for line in self:
            _super = super(AccountMoveLine, line)
            # The super method loop over the lines and returns a list of
            # prepared lines. Here we'll have 1 line per call to super.
            # If we called super on the whole list, we would need to
            # browse again the lines, or match the 'lines' vs
            # 'prepared_lines' to update the transaction_ref.
            vals = _super.prepare_move_lines_for_reconciliation_widget(
                target_currency=target_currency,
                target_date=target_date)[0]
            vals['transaction_ref'] = line.transaction_ref
            prepared_lines.append(vals)
        return prepared_lines

    @api.model
    def domain_move_lines_for_reconciliation(self, excluded_ids=None,
                                             str=False):
        """ Add transaction_ref in search of move lines"""
        _super = super(AccountMoveLine, self)
        _get_domain = _super.domain_move_lines_for_reconciliation
        domain = _get_domain(excluded_ids=excluded_ids, str=str)
        if not str and str != '/':
            return domain
        domain_trans_ref = [('transaction_ref', 'ilike', str)]
        return expression.OR([domain, domain_trans_ref])
