# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Mass Reconcile by Purchase Line",
    "summary": "Allows to reconcile based on the PO line",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "depends": ["account_mass_reconcile", "account_move_line_purchase_info"],
    "license": "AGPL-3",
    "data": ["security/ir.model.access.csv", "views/mass_reconcile.xml"],
    "installable": True,
    "auto_install": False,
}
