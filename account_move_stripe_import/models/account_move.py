# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.addons.account_move_base_import.models.account_move import (
    ErrorTooManyPartner,
)


class AccountMoveCompletionRule(models.Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.move.completion.rule"

    function_to_call = fields.Selection(
        selection_add=[
            (
                "get_from_transaction_ref_and_so",
                "Match Sales Order using transaction Reference",
            ),
        ]
    )

    def get_from_transaction_ref_and_so(self, line):
        """
        Same as get_from_transaction_id_and_so but uses the reference field
        of the transaction instead of its ID.
        """
        res = {}
        so_obj = self.env["sale.order"]
        reference = line.name
        if line.name.startswith("REFUND"):
            # Substring between
            reference = line.name[len("REFUND FOR CHARGE(")+1:-len(")")]
        sales = so_obj.search([("transaction_ids.reference", "=", reference)])
        partners = sales.mapped("partner_id")
        if len(partners) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" was matched by more than ' "one partner.")
                % line.name
            )
        if len(partners) == 1:
            res["partner_id"] = partners.id
            res["account_id"] = partners.property_account_receivable_id.id
        return res
