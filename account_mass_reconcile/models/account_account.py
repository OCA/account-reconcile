# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    skip_invoice_auto_recon = fields.Boolean("Skip Invoice Auto Reconciliation", copy=False)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        return super(AccountMove, self.with_context(skip_invoice_reconciliation=True)).action_post()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self):
        if any(self.mapped('account_id.skip_invoice_auto_recon')) and self._context.get('skip_invoice_reconciliation'):
            return
        return super(AccountMoveLine, self).reconcile()
