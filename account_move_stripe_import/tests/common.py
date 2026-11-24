# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

import stripe

from odoo.addons.account_payment.tests.common import AccountPaymentCommon
from odoo.addons.payment_stripe.tests.common import StripeCommon

STRIPE_MAX_LIMIT = 100
ARRIVAL_DATE_FILTERS = {
    "gt": lambda arrival_date, value: arrival_date > value,
    "gte": lambda arrival_date, value: arrival_date >= value,
    "lt": lambda arrival_date, value: arrival_date < value,
    "lte": lambda arrival_date, value: arrival_date <= value,
}


class FakeStripeAccounts:
    def __init__(self):
        self.payouts_by_key = {}
        self.transactions_by_payout = {}

    def add_payout(self, api_key, payout_id, arrival_date, transactions, status="paid"):
        self.payouts_by_key.setdefault(api_key, []).append(
            {
                "id": payout_id,
                "object": "payout",
                "created": arrival_date - 2 * 86400,
                "arrival_date": arrival_date,
                "status": status,
            }
        )
        self.transactions_by_payout[(api_key, payout_id)] = transactions

    def set_payout_status(self, api_key, payout_id, status):
        for payout in self.payouts_by_key[api_key]:
            if payout["id"] == payout_id:
                payout["status"] = status

    def list_payouts(self, api_key=None, **params):
        self._check_api_key(api_key)
        arrival_date_filters = params.get("arrival_date", {}).items()
        payouts = sorted(
            (
                payout
                for payout in self.payouts_by_key.get(api_key, [])
                if payout["status"] == params.get("status", payout["status"])
                and all(
                    ARRIVAL_DATE_FILTERS[operator](payout["arrival_date"], value)
                    for operator, value in arrival_date_filters
                )
            ),
            key=lambda payout: payout["created"],
            reverse=True,
        )
        return self._page(payouts, api_key, params)

    def list_transactions(self, api_key=None, payout=None, **params):
        self._check_api_key(api_key)
        return self._page(
            self.transactions_by_payout[(api_key, payout)], api_key, params
        )

    def _check_api_key(self, api_key):
        if not api_key:
            raise stripe.AuthenticationError("No API key provided.")

    def _page(self, objects, api_key, params):
        limit = params.get("limit", 10)
        if limit > STRIPE_MAX_LIMIT:
            raise stripe.InvalidRequestError(
                "This value must be less than or equal to 100.", "limit"
            )
        start = 0
        if params.get("starting_after"):
            ids = [obj["id"] for obj in objects]
            start = ids.index(params["starting_after"]) + 1
        return stripe.ListObject.construct_from(
            {
                "object": "list",
                "data": objects[start : start + limit],
                "has_more": start + limit < len(objects),
                "url": "/v1/fake",
            },
            api_key,
        )


def balance_transaction(
    txn_id, amount, txn_type, source, created, description=None, fees=()
):
    return {
        "id": txn_id,
        "object": "balance_transaction",
        "amount": amount,
        "created": created,
        "description": description,
        "source": source,
        "type": txn_type,
        "fee_details": [
            {"amount": fee_amount, "description": fee_description, "type": "stripe_fee"}
            for fee_description, fee_amount in fees
        ],
    }


class StripeImportCommon(StripeCommon, AccountPaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stripe_partner = cls.env["res.partner"].create({"name": "Stripe"})
        cls.stripe_journal = cls._create_stripe_journal(cls.company_data)

    @classmethod
    def _create_stripe_journal(cls, company_data):
        company = company_data["company"]
        return cls.env["account.journal"].create(
            {
                "name": "Stripe",
                "code": "STRP",
                "type": "bank",
                "company_id": company.id,
                "used_for_import": True,
                "import_type": "stripe",
                "partner_id": cls.stripe_partner.id,
                "commission_account_id": company_data["default_account_expense"].id,
                "receivable_account_id": company_data["default_account_receivable"].id,
            }
        )

    def setUp(self):
        super().setUp()
        self.stripe_accounts = FakeStripeAccounts()
        self.startPatcher(
            mock.patch.object(
                stripe.Payout, "list", side_effect=self.stripe_accounts.list_payouts
            )
        )
        self.startPatcher(
            mock.patch.object(
                stripe.BalanceTransaction,
                "list",
                side_effect=self.stripe_accounts.list_transactions,
            )
        )

    def _add_stripe_payout(
        self, payout_id, arrival_date, transactions, provider=None, status="paid"
    ):
        self.stripe_accounts.add_payout(
            (provider or self.stripe).stripe_secret_key,
            payout_id,
            arrival_date,
            transactions,
            status=status,
        )

    def _set_stripe_payout_status(self, payout_id, status, provider=None):
        self.stripe_accounts.set_payout_status(
            (provider or self.stripe).stripe_secret_key, payout_id, status
        )

    def _add_simple_stripe_payout(
        self, payout_id, arrival_date, provider=None, status="paid"
    ):
        self._add_stripe_payout(
            payout_id,
            arrival_date,
            [
                balance_transaction(
                    f"txn_ch_{payout_id}",
                    1000,
                    "charge",
                    f"ch_{payout_id}",
                    arrival_date - 86400,
                    fees=[("Stripe processing fees", 30)],
                ),
                balance_transaction(
                    f"txn_{payout_id}", -970, "payout", payout_id, arrival_date
                ),
            ],
            provider=provider,
            status=status,
        )

    def _run_stripe_import_cron(self):
        self.env.ref(
            "account_move_stripe_import.ir_cron_run_deposit_import"
        ).method_direct_trigger()

    def _stripe_entries(self, journal=None):
        return self.env["account.move"].search(
            [("journal_id", "=", (journal or self.stripe_journal).id)], order="ref"
        )
