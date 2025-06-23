{
    "name": "Partial Reconciliation",
    "version": "17.0.1.0.0",
    "summary": "Allows partial reconciliation between customer invoices and vendor bills.",
    "author": "Areterix Technologies, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Accounting",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_inherit.xml",
        "views/partial_settlement_wizard.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
