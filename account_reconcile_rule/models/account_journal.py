# Copyright 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    def open_reconciliation_rules(self):
        return self.env['ir.actions.act_window'].for_xml_id(
            "account_reconcile_rule",
            "action_account_reconcile_rule"
        )
