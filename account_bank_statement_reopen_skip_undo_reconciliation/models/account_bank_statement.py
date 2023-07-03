# Copyright 2022 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_reopen(self):
        self = self.with_context(skip_undo_reconciliation=True)
        return super(AccountBankStatement, self).button_reopen()
