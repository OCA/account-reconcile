# © 2015-18 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Mass Reconcile by Purchase Line",
    "summary": "Allows to reconcile based on the PO line",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "depends": ["account_mass_reconcile",
                "account_move_line_purchase_info",
                ],
    "license": "AGPL-3",
    "data": [
        "views/mass_reconcile.xml",
    ],
    "installable": True,
    "auto_install": False,
}
