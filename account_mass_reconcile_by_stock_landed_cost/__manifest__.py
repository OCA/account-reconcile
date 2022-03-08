# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Mass Reconcile by Stock Landed Cost",
    "summary": "Allows to reconcile based on the stock landed cost",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "depends": [
        "account_mass_reconcile",
        "account_move_line_landed_cost_info",
    ],
    "license": "AGPL-3",
    "data": ["security/ir.model.access.csv", "views/mass_reconcile.xml"],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["AaronHForgeFlow"],
}
