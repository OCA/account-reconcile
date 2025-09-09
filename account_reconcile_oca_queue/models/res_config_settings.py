# Copyright 2025 Jacques-Etienne Baudoux (BICM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_auto_reconcile_queue = fields.Boolean(
        related="company_id.account_auto_reconcile_queue",
        readonly=False,
    )
