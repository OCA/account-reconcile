# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reconciliation_commit_every = fields.Integer(
        related="company_id.reconciliation_commit_every",
        string="How often to commit when performing automatic reconciliation.",
        help="Leave zero to commit only at the end of the process.",
        readonly=False,
    )


class Company(models.Model):
    _inherit = "res.company"

    reconciliation_commit_every = fields.Integer(
        string="How often to commit when performing automatic reconciliation.",
        help="Leave zero to commit only at the end of the process.",
    )
