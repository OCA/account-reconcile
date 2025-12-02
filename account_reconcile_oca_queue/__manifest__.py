# Copyright 2025 Jacques-Etienne Baudoux (BICM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Oca Queue",
    "summary": """
        Auto-reconcile in queue jobs""",
    "version": "18.0.1.1.0",
    "license": "AGPL-3",
    "author": "BCIM,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": [
        "account_reconcile_oca",
        "queue_job",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
}
