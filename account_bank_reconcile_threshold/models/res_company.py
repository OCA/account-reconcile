# -*- coding: utf-8 -*-
# Copyright 2018 Odoo SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    account_bank_reconciliation_start = fields.Date(
        string="Bank Reconciliation Threshold",
        help="""The bank reconciliation widget won't ask to reconcile
         payments older than this date. This is useful if you install
         accounting after having used invoicing for some time and don't want
         to reconcile all the past payments with bank statements.""")
