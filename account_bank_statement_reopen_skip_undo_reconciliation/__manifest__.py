# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# Copyright 2022 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Bank Statement Reopen Skip Undo Reconciliation",
    "summary": "When reopening a bank statement it will respect the "
    "reconciled entries.",
    "version": "15.0.1.0.1",
    "author": "ForgeFlow, Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "depends": ["account"],
    "data": ["views/account_bank_statement_views.xml"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
