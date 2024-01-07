# © 2015-18 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvanced(models.AbstractModel):
    _inherit = 'mass.reconcile.advanced'

    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get('product_id') and
                    move_line.get('purchase_line_id'))

    @staticmethod
    def _matchers(move_line):
        return (('product_id', move_line['product_id']),
                ('purchase_line_id', move_line['purchase_line_id']))

    @staticmethod
    def _opposite_matchers(move_line):
        yield ('product_id', move_line['product_id'])
        yield ('purchase_line_id', move_line['purchase_line_id'])
