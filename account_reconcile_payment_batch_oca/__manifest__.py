# Copyright 2024 Dixmit
# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Payment Batch OCA",
    "summary": "Allow to reconcile payment/debit order on reconcile widget",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "development_status": "Beta",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_reconcile_oca", "account_payment_batch_oca"],
    "data": [
        "views/account_payment_lot.xml",
        "views/account_bank_statement_line.xml",
    ],
    # This module is only useful if the bank groups the debit/credit on the bank
    # statement for payment orders ; that's why we don't set auto_install=True
}
