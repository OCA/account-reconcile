# -*- coding: utf-8 -*-
# © 2018 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    def write(self, vals):
        if 'reconcile' in vals:
            rec_val = vals.get('reconcile')
            move_lines = self.env['account.move.line'].search(
                [('account_id', 'in', self.ids)])
            if move_lines:
                for acc in self:
                    acc_move_lines = move_lines.filtered(
                        lambda line: line.account_id == acc)
                    self.env.cr.execute(
                        "UPDATE account_account SET reconcile=%s "
                        "WHERE id=%s", (rec_val, acc.id,))
                    acc_move_lines._amount_residual()
                vals.pop('reconcile')
        return super(AccountAccount, self).write(vals=vals)
