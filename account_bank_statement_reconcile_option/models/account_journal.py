# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    bank_reconcile_account_allowed_ids = fields.Many2many(
        "account.account",
        "account_acount_journal_rel",
        "journal_id",
        "account_id",
        help="Only these accounts will be proposed for reconciliation",
    )
    search_limit_days = fields.Integer(
        help="Set here the number of days before and after the bank "
        "transaction on which Journal Items can be proposed for reconciliation",
    )
