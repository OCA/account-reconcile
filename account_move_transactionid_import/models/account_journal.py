# © 2011-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[
            ('generic_csvxls_transaction',
             'Generic .csv/.xls based on SO transaction ID')
        ])
