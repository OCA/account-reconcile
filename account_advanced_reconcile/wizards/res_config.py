# -*- coding: utf-8 -*-
# © 2012-2014 Camptocamp SA - Guewen Baconnier

from openerp import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    reconciliation_commit_every = fields.Integer(
            related='company_id.reconciliation_commit_every')

    @api.one
    @api.depends('company_id')
    def _company_onchange(self):
        self.reconciliation_commit_every = \
            self.company_id.reconciliation_commit_every


class Company(models.Model):
    _inherit = "res.company"

    reconciliation_commit_every = fields.Integer(
            string='How often to commit when performing automatic '
            'reconciliation.',
            help="""Leave zero to commit only at the end of the process.""")
