# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.model
    def create(self, vals):
        line = super().create(vals)
        if not self.env.context.get('skip_postprocess'):
            line \
                .with_context(postprocess_on_import=True) \
                .action_apply_postprocessing()
        return line

    @api.multi
    def action_apply_postprocessing(self):
        postprocess_on_import = self.env.context.get('postprocess_on_import')
        models = self.env["account.bank.statement.postprocess.model"].search(
            [('apply_on_import', '=', True)] if postprocess_on_import else []
        )
        for line in self:
            if line.journal_entry_ids.ids:
                continue
            models.apply(line)
