# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    exclude_from_bank_statement_reconciliation = fields.Boolean(
        string="Exclude from Bank Statement Reconciliation", default=False,
        help="Mark this if you want to prevent account move lines from this "
             "account to be proposed in the bank statement reconciliation.")
