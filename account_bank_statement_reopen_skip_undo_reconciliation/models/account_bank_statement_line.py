# Copyright 2022 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def button_undo_reconciliation(self):
        if self._context.get("skip_undo_reconciliation"):
            return
        res = super(AccountBankStatementLine, self).button_undo_reconciliation()
        if self.statement_id.state == "open":
            self.move_id.button_draft()
        return res
