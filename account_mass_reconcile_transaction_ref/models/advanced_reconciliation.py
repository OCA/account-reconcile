# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, models


class MassReconcileAdvancedTransactionRef(models.TransientModel):

    _name = 'mass.reconcile.advanced.transaction.ref'
    _inherit = 'mass.reconcile.advanced'

    @api.multi
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get('transaction_ref') and
                    move_line.get('partner_id'))

    @api.multi
    def _matchers(self, move_line):
        return (('partner_id', move_line['partner_id']),
                ('ref', move_line['transaction_ref'].lower().strip()))

    @api.multi
    def _opposite_matchers(self, move_line):
        yield ('partner_id', move_line['partner_id'])
        yield ('ref', (move_line['transaction_ref'] or '').lower().strip())


class MassReconcileAdvancedTransactionRefVsRef(models.TransientModel):

    _name = 'mass.reconcile.advanced.transaction.ref.vs.ref'
    _inherit = 'mass.reconcile.advanced'

    @api.multi
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get('ref') and move_line.get('partner_id'))

    @api.multi
    def _matchers(self, move_line):
        return (('partner_id', move_line['partner_id']),
                ('ref', move_line['ref'].lower().strip()))

    @api.multi
    def _opposite_matchers(self, move_line):
        yield ('partner_id', move_line['partner_id'])
        yield ('ref', (move_line['transaction_ref'] or '').lower().strip())
