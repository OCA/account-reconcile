# Copyright 2011-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import _, fields, models

from odoo.addons.account_move_base_import.models.account_move import ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):

    _name = "account.move.completion.rule"
    _inherit = "account.move.completion.rule"

    function_to_call = fields.Selection(
        selection_add=[
            ("get_from_name_and_so", "From line name (based on SO number)"),
            (
                "get_from_name_and_so_payment_ref",
                "From line name (based on SO payment ref)",
            ),
        ]
    )

    # Should be private but data are initialized with no update XML
    def get_from_name_and_so(self, line):
        """
        Match the partner based on the SO number and the reference of the
        statement line. Then, call the generic get_values_for_line method to
        complete other values. If more than one partner matched, raise the
        ErrorTooManyPartner error.

        :param int/long st_line: read of the concerned
        account.bank.statement.line

        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        return self._get_from_name_and_so_generic(line, "name")

    # Should be private but data are initialized with no update XML
    def get_from_name_and_so_payment_ref(self, line):
        """
        :param int/long st_line: read of the concerned
        account.bank.statement.line

        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        return self._get_from_name_and_so_generic(line, "reference")

    def _get_from_name_and_so_generic(self, line, search_by):
        res = {}
        so_obj = self.env["sale.order"]
        orders = so_obj.search([(search_by, "=", line.name)])
        if len(orders) > 1:
            raise ErrorTooManyPartner(
                _(
                    'Line named "%s" was matched by more '
                    "than one partner while looking on SO by ref."
                )
                % line.name
            )
        if len(orders) == 1:
            res["partner_id"] = orders[0].partner_id.id
        return res
