# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account financial discount reconciliation widget OCA",
    "version": "14.0.1.0.0",
    "category": "Account",
    "website": "camptocamp.com",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account_financial_discount", "account_reconciliation_widget", "account_reconcile_model_strict_match_amount"],
    "data": [
        "views/assets.xml",
        "views/account_reconcile_model.xml",
    ],
    "qweb": ["static/src/xml/reconciliation_templates.xml"],
}
