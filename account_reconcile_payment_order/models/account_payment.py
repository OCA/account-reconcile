# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    maturity_order_id = fields.Many2one(comodel_name="account.payment.order.maturity")
