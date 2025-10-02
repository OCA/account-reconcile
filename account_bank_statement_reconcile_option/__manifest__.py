# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Account Bank Statement Reconcile Options",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Give options on the reconciliation propositions",
    "author": "La Louve, Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "license": "AGPL-3",
    "depends": [
        "account_reconcile_oca",
        "base_view_inheritance_extension",  # to able to update the context of a field
    ],
    "data": [
        "views/account_bank_statement_line.xml",
        "views/account_journal.xml",
    ],
    "installable": True,
}
