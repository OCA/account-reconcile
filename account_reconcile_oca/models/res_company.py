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
    reconcile_invoices_past_months_limit = fields.Integer(
        default=18,
        help="Number of months in the past to consider when searching for "
        "invoices and bills to reconcile automatically.",
    )
    reconcile_invoices_auto_reconcile = fields.Boolean(
        help="Automatically reconcile a bank statement line when a matching "
        "invoice or bill is found.",
    )
    reconcile_invoices_unique_matching = fields.Boolean(
        help="Only reconcile automatically when exactly one matching invoice "
        "or bill is found.",
    )
    reconcile_invoices_match_partner = fields.Boolean(
        help="Only consider invoices and bills whose partner matches the partner "
        "of the bank statement line."
    )
    reconcile_invoices_match_partner_ids = fields.Many2many(
        string="Auto-reconcile Invoices Matching partners",
        comodel_name="res.partner",
        help="Restrict partner matching to bank statement lines belonging to "
        "the selected partners.",
    )
    reconcile_invoices_match_partner_category_ids = fields.Many2many(
        comodel_name="res.partner.category",
        help="Restrict partner matching to bank statement lines whose partner "
        "belongs to one of the selected categories.",
    )
    reconcile_invoices_match_text = fields.Boolean(
        help="Only consider invoices and bills whose reference or label matches "
        "the payment reference of the bank statement line.",
    )

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
