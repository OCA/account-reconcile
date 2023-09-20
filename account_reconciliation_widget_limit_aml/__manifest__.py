# Copyright 2023 Valentin Vinagre <valentin.vinagre@sygel.es>
# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Reconciliation Widget Limit AML",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Filter all account move lines in reconciliation view",
    "author": "Sygel, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_reconciliation_widget"],
    "data": ["views/res_config_settings_views.xml"],
    "installable": True,
}
