# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Bank Statement Check Number",
    "summary": "Add the check number in the bank statements",
    "version": "16.0.1.0.0",
    "depends": ["account_move_line_check_number", "account_statement_base"],
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Accounting & Finance",
    "data": ["views/account_bank_statement_views.xml"],
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["ps-tubtim"],
}
