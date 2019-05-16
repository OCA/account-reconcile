# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Bank Statement Partner Find Fuzzy",
    "summary": "Search partners in bank statement lines using fuzzy search",
    "version": "12.0.1.0.0",
    "depends": ["base_search_fuzzy", "account"],
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "http://www.github.com/OCA/account-reconcile",
    "category": "Finance",
    "data": [
        "data/trgm_index_data.xml",
    ],
    'license': 'AGPL-3',
    "auto_install": False,
    'installable': True,
}
