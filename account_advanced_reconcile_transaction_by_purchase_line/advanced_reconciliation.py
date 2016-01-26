# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele. Copyright Camptocamp SA
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


class EasyReconcileAdvancedTransactionByPurchaseLine(models.TransientModel):

    _name = 'easy.reconcile.advanced.by.purchase.line'
    _inherit = 'easy.reconcile.advanced'

    @api.model
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not move_line.get('partner_id') and move_line.get(
                'product_id') and move_line.get('purchase_line_id')

    @api.model
    def _matchers(self, move_line):
        return (('partner_id', move_line['partner_id']),
                ('product_id', move_line['product_id']),
                ('purchase_line_id', move_line['purchase_line_id']))

    @api.model
    def _opposite_matchers(self, move_line):
        yield ('partner_id', (move_line['partner_id']))
        yield ('product_id', (move_line['product_id']))
        yield ('purchase_line_id', (move_line['purchase_line_id']))
