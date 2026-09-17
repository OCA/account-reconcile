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
    # reconcile fields conditions
    reconcile_invoices_past_months_limit = fields.Integer(default=18)
    reconcile_invoices_auto_reconcile = fields.Boolean()
    reconcile_invoices_unique_matching = fields.Boolean()
    reconcile_invoices_match_partner = fields.Boolean()
    reconcile_invoices_match_partner_ids = fields.Many2many(
        string="Auto-reconcile Invoices Matching partners", comodel_name="res.partner"
    )
    reconcile_invoices_match_partner_category_ids = fields.Many2many(
        comodel_name="res.partner.category"
    )
    reconcile_invoices_match_same_currency = fields.Boolean(default=True)
    reconcile_invoices_match_text = fields.Boolean()

    def _get_unreconciled_statement_lines_redirect_action(
        self, unreconciled_statement_lines
    ):
        """Define the appropriate views that this method will have, by default the
        account module does not add any.
        """
        action = super()._get_unreconciled_statement_lines_redirect_action(
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
