# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import fields, models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    maturity_order_ids = fields.One2many(
        comodel_name="account.payment.order.maturity", inverse_name="payment_order_id"
    )

    def generated2uploaded(self):
        result = super().generated2uploaded()
        for record in self:
            vals = sorted(
                self.payment_ids.read(["id", "payment_line_date", "currency_id"]),
                key=lambda r: (r["payment_line_date"], r["currency_id"][0]),
            )
            for key, _group in groupby(
                vals, lambda x: (x["payment_line_date"], x["currency_id"][0])
            ):
                self.env["account.payment.order.maturity"].create(
                    {
                        "payment_order_id": record.id,
                        "currency_id": key[1],
                        "date": key[0],
                        "payment_ids": [
                            (
                                6,
                                0,
                                record.payment_ids.filtered(
                                    lambda r: r.payment_line_date == key[0]
                                    and r.currency_id.id == key[1]
                                ).ids,
                            )
                        ],
                    }
                )
        return result

    def action_uploaded_cancel(self):
        self.maturity_order_ids.unlink()
        return super().action_cancel()
