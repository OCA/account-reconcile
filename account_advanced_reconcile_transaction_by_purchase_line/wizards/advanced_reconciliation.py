# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
