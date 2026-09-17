# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reconcile_aggregate = fields.Selection(
        related="company_id.reconcile_aggregate", readonly=False
    )
    reconcile_invoices_past_months_limit = fields.Integer(
        related="company_id.reconcile_invoices_past_months_limit", readonly=False
    )
    reconcile_invoices_auto_reconcile = fields.Boolean(
        related="company_id.reconcile_invoices_auto_reconcile", readonly=False
    )
    reconcile_invoices_unique_matching = fields.Boolean(
        related="company_id.reconcile_invoices_unique_matching", readonly=False
    )
    reconcile_invoices_match_partner = fields.Boolean(
        related="company_id.reconcile_invoices_match_partner", readonly=False
    )
    reconcile_invoices_match_partner_ids = fields.Many2many(
        related="company_id.reconcile_invoices_match_partner_ids", readonly=False
    )
    reconcile_invoices_match_partner_category_ids = fields.Many2many(
        related="company_id.reconcile_invoices_match_partner_category_ids",
        readonly=False,
    )
    reconcile_invoices_match_same_currency = fields.Boolean(
        related="company_id.reconcile_invoices_match_same_currency", readonly=False
    )
    reconcile_invoices_match_text = fields.Boolean(
        related="company_id.reconcile_invoices_match_text",
        readonly=False,
    )
