# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ResPartner(models.Model):
    """Add a bank label on the partner so that we can use it to match
    this partner when we found this in a statement line.
    """

    _inherit = "res.partner"

    bank_statement_label = fields.Char(
        string="Bank Statement Label",
        help="Enter the various label found on your bank statement "
        "separated by a ; If one of this label is include in the "
        "bank statement line, the partner will be automatically "
        "filled (as long as you use this method/rules in your "
        "statement profile).",
    )
