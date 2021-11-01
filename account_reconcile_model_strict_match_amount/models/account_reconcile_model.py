# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountReconcileModel(models.Model):

    _inherit = "account.reconcile.model"

    strict_match_total_amount = fields.Boolean(
        string="Strict Amount Matching",
        help="Avoid bypassing the Amount Matching parameter in case of a "
        "statement line communication matching exactly existing entries.",
    )

    # flake8: noqa
    def _get_select_communication_flag(self):
        comm_flag = super()._get_select_communication_flag()
        if not self.match_total_amount or not self.strict_match_total_amount:
            return comm_flag
        # comm_flag.replace is for 13.0
        comm_flag = (
            r"""
            COALESCE(
            """
            + comm_flag.replace("AS communication_flag", "")
            + r"""
            , FALSE)
            AND
            CASE
                WHEN abs(st_line.amount) < abs(aml.balance) THEN abs(st_line.amount) / abs(aml.balance) * 100
                WHEN abs(st_line.amount) > abs(aml.balance) THEN abs(aml.balance) / abs(st_line.amount) * 100
                ELSE 100
            END >= {match_total_amount_param}
        """.format(
                match_total_amount_param=self.match_total_amount_param
            )
        )
        return comm_flag

    def _get_select_payment_reference_flag(self):
        ref_flag = super()._get_select_payment_reference_flag()
        if not self.match_total_amount or not self.strict_match_total_amount:
            return ref_flag
        # ref_flag.replace is for 13.0
        ref_flag = (
            r"""
            COALESCE(
            """
            + ref_flag.replace("AS reference_flag", "")
            + r"""
            , FALSE)
            AND
            CASE
                WHEN abs(st_line.amount) < abs(aml.balance) THEN abs(st_line.amount) / abs(aml.balance) * 100
                WHEN abs(st_line.amount) > abs(aml.balance) THEN abs(aml.balance) / abs(st_line.amount) * 100
                ELSE 100
            END >= {match_total_amount_param}
        """.format(
                match_total_amount_param=self.match_total_amount_param
            )
        )
        return ref_flag
