# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
from openerp.osv import orm, fields


class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'transaction_ref': fields.char('Transaction Ref.',
                                       select=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['transaction_ref'] = False
        _super = super(account_move_line, self)
        return _super.copy_data(cr, uid, id, default=default, context=context)

    def prepare_move_lines_for_reconciliation_widget(self, cr, uid, lines,
                                                     target_currency=False,
                                                     target_date=False,
                                                     context=None):
        _super = super(account_move_line, self)
        prepare = _super.prepare_move_lines_for_reconciliation_widget
        prepared_lines = []
        for line in lines:
            # The super method loop over the lines and returns a list of
            # prepared lines. Here we'll have 1 line per call to super.
            # If we called super on the whole list, we would need to
            # browse again the lines, or match the 'lines' vs
            # 'prepared_lines' to update the transaction_ref.
            vals = prepare(cr, uid, [line], target_currency=target_currency,
                           target_date=target_date, context=context)[0]
            vals['transaction_ref'] = line.transaction_ref
            prepared_lines.append(vals)
        return prepared_lines
