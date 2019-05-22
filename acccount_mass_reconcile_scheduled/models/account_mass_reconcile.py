# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class AccountMassReconcile(models.Model):

    _inherit = 'account.mass.reconcile'

    scheduled_run = fields.Boolean(
        string='Run by scheduled task',
        help='Check this box to make this mass reconcile selected by the '
             'scheduled task "Run scheduled mass reconcile".'
    )

    @api.model
    def _cron_run_scheduled_mass_reconcile(self):
        mass_reconciles = self.search([('scheduled_run', '=', True)])
        for mass_reconcile in mass_reconciles:
            mass_reconcile.run_reconcile()
