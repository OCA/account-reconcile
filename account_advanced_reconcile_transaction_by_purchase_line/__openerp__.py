# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Advanced Reconcile Transaction by Purchase Line",
    "summary": "Allows to reconcile based on the PO line",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic",
    "depends": ["account_advanced_reconcile",
                "account_move_line_purchase_info"
    ],
    "license": "AGPL-3",
    "data": [
        "views/easy_reconcile_view.xml",
    ],
    'installable': True,
}
