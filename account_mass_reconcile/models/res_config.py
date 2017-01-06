# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Leonardo Pistone, Damien Crier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    reconciliation_commit_every = fields.Integer(
        related="company_id.reconciliation_commit_every",
        string="How often to commit when performing automatic "
        "reconciliation.",
        help="Leave zero to commit only at the end of the process."
    )


class Company(models.Model):
    _inherit = "res.company"

    reconciliation_commit_every = fields.Integer(
        string="How often to commit when performing automatic "
        "reconciliation.",
        help="Leave zero to commit only at the end of the process."
    )
