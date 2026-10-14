from odoo import fields, models


class AccountAccountReconcileData(models.TransientModel):
    _name = "account.account.reconcile.data"
    _description = "Reconcile data model to store user info"

    user_id = fields.Many2one("res.users", required=True)
    reconcile_id = fields.Integer(required=True)
    data = fields.Json()
