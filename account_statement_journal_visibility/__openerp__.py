# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Control Statement Visibility Based On Groups",
    "version": "8.0.1.0.0",
    "category": "Finance",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "datas/ir_actions_server_data.xml",
        "views/account_journal_views.xml",
        "views/account_bank_statement_views.xml",
    ],
}
