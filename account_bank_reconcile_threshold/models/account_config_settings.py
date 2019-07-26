# -*- coding: utf-8 -*-
# Copyright 2018 Odoo SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    account_bank_reconciliation_start = fields.Date(
        string="Bank Reconciliation Threshold",
        related='company_id.account_bank_reconciliation_start',
        readonly=False,
        help="""The bank reconciliation widget won't ask to reconcile payments
        older than this date. This is useful if you install accounting
        after having used invoicing for some time and don't want to
        reconcile all the past payments with bank statements.""")
