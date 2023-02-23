from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    skip_remove_reconciliation = fields.Boolean(
        help="Do not unlink the reconciliation when an account move is set to draft."
    )
