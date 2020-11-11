# Copyright 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Early Payment Discount Reconciliation Rules",
    "version": "13.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account_reconcile_rule", "account_early_payment_discount"],
    "website": "https://github.com/OCA/account-reconcile",
    "data": ["views/account_reconcile_rule_view.xml"],
    "installable": True,
    "auto_install": True,
}
