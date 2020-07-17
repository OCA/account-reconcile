# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools.translate import _


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    def button_journal_items(self):
        return {
            "name": _("Journal Items"),
            "view_mode": "tree,form",
            "res_model": "account.move.line",
            "views": [
                (self.env.ref("account.view_move_line_tree").id, "tree"),
                (self.env.ref("account.view_move_line_form").id, "form"),
            ],
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.mapped("move_line_ids").ids)],
            "context": {"journal_id": self.journal_id.id},
        }
