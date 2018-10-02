# © 2018 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    def write(self, vals):
        reconcile = False
        if vals.get('reconcile', False) and not self.env.context.get(
                'set_reconcilable', False):
            reconcile = vals.pop('reconcile')
        rec = super(AccountAccount, self).write(vals=vals)
        if reconcile:
            moves_lines = self.env['account.move.line'].search(
                [('account_id', 'in', self.ids)])
            for account in self:
                lines = moves_lines.filtered(
                    lambda line: line.account_id == account)
                if lines:
                    t_account = account.copy()
                    lines.write({'account_id': t_account.id})
                    account.with_context(set_reconcilable=True).write(
                        {'reconcile': reconcile})
                    lines.write({'account_id': account.id})
                    lines._amount_residual()
                    t_account.unlink()
        return rec
