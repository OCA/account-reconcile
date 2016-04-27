# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
#             Joel Grand-Guillaume, Nicolas Bessi, Matthieu Dietrich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class ResPartner(models.Model):
    """Add a bank label on the partner so that we can use it to match
    this partner when we found this in a statement line.
    """
    _inherit = 'res.partner'

    bank_statement_label = fields.Char(
        string='Bank Statement Label',
        size=100,
        help="Enter the various label found on your bank statement "
        "separated by a ; If one of this label is include in the "
        "bank statement line, the partner will be automatically "
        "filled (as long as you use this method/rules in your "
        "statement profile).")
