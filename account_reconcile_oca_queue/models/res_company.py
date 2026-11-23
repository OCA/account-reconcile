# Copyright 2025 Jacques-Etienne Baudoux (BICM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_auto_reconcile_queue = fields.Boolean(
        string="Auto reconcile in background",
        help="Auto reconcile using queue jobs",
        default=False,
    )
