# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Stripe Import",
    "summary": "Import Deposit/Payout details from Stripe",
    "version": "18.0.1.0.0",
    "category": "Finance",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_move_base_import", "payment_stripe", "sale"],
    "external_dependencies": {"python": ["stripe"]},
    "data": [
        "wizards/credit_statement_import_views.xml",
        "data/cron.xml",
        "data/completion_rule_data.xml",
    ],
}
