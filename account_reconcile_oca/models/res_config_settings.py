# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reconcile_aggregate = fields.Selection(
        related="company_id.reconcile_aggregate", readonly=False
    )
    show_reconcile_button_with_no_entries_to_reconcile = fields.Boolean(
        related="company_id.show_reconcile_button_with_no_entries_to_reconcile",
        readonly=False,
    )
