# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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

from openerp import models, api


class account_statement_from_invoice_lines(models.TransientModel):

    _inherit = "account.statement.from.invoice.lines"

    @api.multi
    def populate_statement(self):
        """
        Inverse data from account_move_line
        bank_statement_line.name = line.ref
        bank_statement_line.ref = name.name
        """
        super(account_statement_from_invoice_lines, self).populate_statement()
        bank_statement_obj = self.env['account.bank.statement']
        statement_id = self._context.get('statement_id', False)

        if statement_id:
            statement = bank_statement_obj.browse(statement_id)
            for line in statement.line_ids:
                line.write({'name': line.ref, 'ref': line.name})

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
