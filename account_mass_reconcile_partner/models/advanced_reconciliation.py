# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api


class MassReconcileAdvancedPartnerChrono(models.TransientModel):

    _name = 'mass.reconcile.advanced.partner'
    _inherit = 'mass.reconcile.advanced'

    @api.multi
    def _get_filter(self):
        """Order move lines by date for chronological processing"""
        where, params = super(
            MassReconcileAdvancedPartnerChrono, self)._get_filter()
        where = "%s ORDER BY date ASC, id ASC" % where
        return where, params

    @api.multi
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not move_line.get('partner_id')

    @api.multi
    def _matchers(self, move_line):
        """Match only the partner"""
        return [('partner_id', move_line['partner_id']), ]

    @api.multi
    def _opposite_matchers(self, move_line):
        """Match only the partner"""
        yield ('partner_id', move_line['partner_id'])
