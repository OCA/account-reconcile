# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    _SELECTION_RECONCILE_MODE = [
        ('normal', 'Normal'),
        ('journal_account', 'Journal Accounts'),
    ]

    set_default_reconcile_partner = fields.Boolean()

    # Column Section
    reconcile_mode = fields.Selection(
        selection=_SELECTION_RECONCILE_MODE, default='normal', required=True,
        string='Reconciliation Mode',
        help=("Change the reconciliation proposition.\n"
              " 'Normal': default behaviour of Odoo;\n"
              " 'Journal Accounts', reconciliation wizard will propose only account"
              " move lines with accounts defined in debit / credit accounting"
              " setting of the current journal."),
    )
    bank_reconcile_account_allowed_ids = fields.Many2many(
        'account.account',
        'account_acount_journal_rel',
        'journal_id',
        'account_id',
        string='Bank Reconcile Account Allowed'
    )
    search_limit_days = fields.Integer(
        string='Search Limit Days',
        help="Set here the number of days before and after the bank "
        "transaction on which Journal Items can be proposed for reconciliation",
        default=0
    )
