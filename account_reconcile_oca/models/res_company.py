# Copyright 2024 Dixmit
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    reconcile_aggregate = fields.Selection(
        selection=lambda self: self.env["account.journal"]
        ._fields["reconcile_aggregate"]
        .selection
    )

    def _get_fiscalyear_lock_statement_lines_redirect_action(
        self, unreconciled_statement_lines
    ):
        """Define the appropriate views that this method will have, by default the
        account module does not add any.
        """
        action = super()._get_fiscalyear_lock_statement_lines_redirect_action(
            unreconciled_statement_lines
        )
        if len(unreconciled_statement_lines) == 1:
            custom_action = self.env["ir.actions.actions"]._for_xml_id(
                "account_reconcile_oca.action_bank_statement_line_create"
            )
            action.update(views=custom_action["views"])
        else:
            custom_action = self.env["ir.actions.actions"]._for_xml_id(
                "account_reconcile_oca.action_bank_statement_line_reconcile_all"
            )
            action.update(
                view_mode=custom_action["view_mode"],
                views=custom_action["views"],
            )
        return action
