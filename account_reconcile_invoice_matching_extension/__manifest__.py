# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Invoice Matching Extension",
    "version": "14.0.1.0.0",
    "category": "Services/Timesheets",
    "summary": "Kaelin Account",
    "description": """
This module extends invoice matching for account reconciliation by allowing users to:
  1. Set a day limit for how far back the reconciliation model applies.
  2. Match invoices based on a given payment term.
It is especially helpful for automating reconciliation processes such as Skonto invoices.
    """,
    "author": "elego Software Solutions GmbH",
    "depends": [
        "account",
        "account_cash_discount_base",
    ],
    "data": [
        "views/account_reconcile_model_views.xml",
    ],
    "demo": [],
    "qweb": [],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
