# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Model Oca",
    "summary": """
        This includes the logic moved from Odoo Community to Odoo Enterprise""",
    "version": "18.0.1.1.0",
    "license": "LGPL-3",
    "author": "Dixmit,Odoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account"],
    "excludes": ["account_accountant"],
    "data": [
        "views/account_reconcile_model_views.xml",
    ],
    "demo": [],
}
