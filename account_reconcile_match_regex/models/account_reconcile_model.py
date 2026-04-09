# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import fields, models


class AccountReconcileModel(models.Model):

    _inherit = "account.reconcile.model"

    match_invoice_regex = fields.Char(
        help="Regex to match the invoice number in the payment reference. "
        "It will be used to identify the invoice associated with a payment."
    )

    def _get_st_line_text_values_for_matching(self, st_line):
        """Override to add the payment reference as a value to match with the regex."""
        values = super()._get_st_line_text_values_for_matching(st_line)
        if not self.match_invoice_regex:
            return values
        result = []
        for value in values:
            if found_value := re.search(self.match_invoice_regex, value):
                groups = found_value.groups()
                if not groups:
                    # We are assuming that the regex does not contains groups in this case
                    groups = [found_value.group(0)]
                for group in groups:
                    result.append(group)
        return result
