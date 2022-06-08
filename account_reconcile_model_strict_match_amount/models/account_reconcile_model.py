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
        if not self.match_total_amount or not self.strict_match_total_amount:
            return super()._get_select_communication_flag()
        else:
            return r"""
                -- Determine a matching or not with the statement line communication using the aml.name, move.name or move.ref.
                COALESCE(
                (
                    aml.name IS NOT NULL
                    AND
                    substring(REGEXP_REPLACE(aml.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*') != ''
                    AND
                        regexp_split_to_array(substring(REGEXP_REPLACE(aml.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'),'\s+')
                        && regexp_split_to_array(substring(REGEXP_REPLACE(st_line.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                )
                OR
                    regexp_split_to_array(substring(REGEXP_REPLACE(move.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'),'\s+')
                    && regexp_split_to_array(substring(REGEXP_REPLACE(st_line.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                OR
                (
                    move.ref IS NOT NULL
                    AND
                    substring(REGEXP_REPLACE(move.ref, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*') != ''
                    AND
                        regexp_split_to_array(substring(REGEXP_REPLACE(move.ref, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'),'\s+')
                        && regexp_split_to_array(substring(REGEXP_REPLACE(st_line.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                )
                , FALSE)
                AND
                CASE
                    WHEN abs(st_line.amount) < abs(aml.balance) THEN abs(st_line.amount) / abs(aml.balance) * 100.0
                    WHEN abs(st_line.amount) > abs(aml.balance) THEN abs(aml.balance) / abs(st_line.amount) * 100.0
                    ELSE 100.0
                END >= {match_total_amount_param} AS communication_flag
            """.format(
                match_total_amount_param=self.match_total_amount_param
            )

    def _get_select_payment_reference_flag(self):
        if not self.match_total_amount or not self.strict_match_total_amount:
            return super()._get_select_payment_reference_flag()
        else:
            return r"""
                -- Determine a matching or not with the statement line communication using the move.invoice_payment_ref.
                COALESCE
                (
                    move.invoice_payment_ref IS NOT NULL
                    AND
                    regexp_replace(move.invoice_payment_ref, '\s+', '', 'g') = regexp_replace(st_line.name, '\s+', '', 'g')
                , FALSE)
                AND
                CASE
                    WHEN abs(st_line.amount) < abs(aml.balance) THEN abs(st_line.amount) / abs(aml.balance) * 100.0
                    WHEN abs(st_line.amount) > abs(aml.balance) THEN abs(aml.balance) / abs(st_line.amount) * 100.0
                    ELSE 100.0
                END >= {match_total_amount_param} AS payment_reference_flag
            """.format(
                match_total_amount_param=self.match_total_amount_param
            )
