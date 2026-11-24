# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict
from datetime import date, datetime, timezone

from odoo import api, fields, models

from odoo.addons.account_move_base_import.parser.parser import AccountMoveImportParser

_logger = logging.getLogger(__name__)

STRIPE_PAGE_LIMIT = 100
UNSETTLED_PAYOUT_STATUSES = ("pending", "in_transit")

try:
    import stripe
except ImportError:
    _logger.debug("Can not import stripe")


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(selection_add=[("stripe", "Stripe")])

    @api.model
    def run_import_stripe_deposit(self):
        for journal in self.search([("import_type", "=", "stripe")]):
            try:
                with self.env.cr.savepoint():
                    journal.multi_move_import(None, None)
            except Exception:
                _logger.exception(
                    "Stripe import failed for journal %s", journal.display_name
                )


class StripeParser(AccountMoveImportParser):
    def __init__(self, journal, *args, **kwargs):
        super().__init__(journal, *args, **kwargs)
        self.env = journal.env

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == "stripe"

    def _get_account(self):
        Provider = self.env["payment.provider"].sudo()
        return Provider.search(
            [("code", "=", "stripe"), ("company_id", "=", self.journal.company_id.id)],
            limit=1,
        )

    def _skip(self, payout_id):
        return bool(self.env["account.move"].search([("ref", "=", payout_id)]))

    def _list_all(self, resource, **params):
        objects = []
        while True:
            results = resource.list(limit=STRIPE_PAGE_LIMIT, **params)["data"]
            if not results:
                break
            objects += results
            params["starting_after"] = results[-1]["id"]
        return objects

    def _get_payout(self, api_key=None):
        kwargs = {}
        if self.journal.last_import_date:
            timestamp = self.journal.last_import_date.replace(
                tzinfo=timezone.utc
            ).timestamp()
            kwargs["arrival_date"] = {"gte": int(timestamp)}
        payouts = self._list_all(stripe.Payout, api_key=api_key, **kwargs)
        if payouts:
            self.journal.last_import_date = datetime.fromtimestamp(
                self._get_resume_arrival_date(payouts)
            )
        paid_payouts = [payout for payout in payouts if payout["status"] == "paid"]
        paid_payouts.reverse()
        return paid_payouts

    def _get_resume_arrival_date(self, payouts):
        resume_arrival_dates = [
            payout["arrival_date"]
            for payout in payouts
            if payout["status"] in UNSETTLED_PAYOUT_STATUSES
        ]
        settled_arrival_dates = [
            payout["arrival_date"]
            for payout in payouts
            if payout["status"] not in UNSETTLED_PAYOUT_STATUSES
        ]
        if settled_arrival_dates:
            resume_arrival_dates.append(max(settled_arrival_dates))
        return min(resume_arrival_dates)

    def parse(self, filebuffer):
        api_key = self._get_account().stripe_secret_key
        for payout in self._get_payout(api_key=api_key):
            if self._skip(payout["id"]):
                continue
            self.move_ref = payout["id"]
            self.move_date = date.fromtimestamp(payout["arrival_date"])
            self.result_row_list = self._list_all(
                stripe.BalanceTransaction, payout=payout["id"], api_key=api_key
            )
            fee_vals = defaultdict(float)
            for line in self.result_row_list:
                for fee in line["fee_details"]:
                    fee_vals[fee["description"]] += fee["amount"]
            for description, amount in fee_vals.items():
                self.result_row_list.append(
                    {
                        "description": description,
                        "amount": -amount,
                        "created": payout["arrival_date"],
                        "type": "fee",
                        "source": None,
                    }
                )
            yield self.result_row_list

    def get_move_line_vals(self, line, *args, **kwargs):
        amount = line["amount"] / 100.0
        vals = {
            "name": line["description"] or line["source"],
            "date_maturity": date.fromtimestamp(line["created"]),
            "credit": amount > 0.0 and amount or 0.0,
            "debit": amount < 0.0 and -amount or 0.0,
            "ref": line["source"],
            "already_completed": False,
            "partner_id": None,
            "account_id": None,
        }
        if line["type"] in ["transfer", "payout"]:
            vals.update(
                {
                    "partner_id": self.journal.partner_id.id,
                    "account_id": self.journal.default_account_id.id,
                    "already_completed": True,
                }
            )
        elif line["type"] == "fee":
            vals.update(
                {
                    "partner_id": self.journal.partner_id.id,
                    "account_id": self.journal.commission_account_id.id,
                    "already_completed": True,
                }
            )
        return vals
