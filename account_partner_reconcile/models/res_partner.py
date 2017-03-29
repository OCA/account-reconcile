# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def action_open_reconcile(self):
        # Open reconciliation view for customers
        accounts = self.env['account.account']
        accounts += (self.property_account_receivable_id +
                     self.property_account_payable_id)

        action_context = {'show_mode_selector': True,
                          'partner_ids': [self.id, ],
                          'account_ids': accounts.ids}
        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
            'context': action_context,
        }
