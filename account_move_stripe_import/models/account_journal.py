# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.account_move_base_import.parser.parser import\
    AccountMoveImportParser
from datetime import date
from collections import defaultdict
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

try:
    import stripe
except ImportError:
    _logger.debug('Can not import stripe')


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    import_type = fields.Selection(selection_add=[('stripe', 'Stripe')])

    @api.model
    def run_import_stripe_deposit(self):
        for journal in self.search([('import_type', '=', 'stripe')]):
            journal.multi_move_import(None, None)


class StripeParser(AccountMoveImportParser):

    def __init__(self, journal, *args, **kwargs):
        super(StripeParser, self).__init__(journal, *args, **kwargs)
        self.env = journal.env

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == 'stripe'

    def _get_account(self):
        return self.env['keychain.account'].sudo().retrieve([
            ('namespace', '=', 'stripe')])[0]

    def _skip(self, payout_id):
        return bool(self.env['account.move'].search([
            ('ref', '=', payout_id)]))

    def _get_payout(self, api_key=None):
        payouts = []
        kwargs = {
            'status': 'paid',
            'limit': 100,
            }
        if self.journal.last_import_date:
            timestamp = datetime.strptime(
                self.journal.last_import_date,
                DEFAULT_SERVER_DATETIME_FORMAT).strftime("%s")
            kwargs['arrival_date'] = {'gt': timestamp}
        while True:
            results = stripe.Payout.list(api_key=api_key, **kwargs)['data']
            if not results:
                break
            payouts += results
            kwargs['starting_after'] = results[-1]['id']
        if payouts:
            payouts.reverse()
            self.journal.last_import_date = date.fromtimestamp(
                payouts[-1]['arrival_date'])
        return payouts

    def parse(self, filebuffer):
        api_key = self._get_account().get_password()
        for payout in self._get_payout(api_key=api_key):
            if self._skip(payout['id']):
                continue
            self.move_ref = payout['id']
            self.move_date = date.fromtimestamp(payout['arrival_date'])
            self.result_row_list = stripe.BalanceTransaction.all(
                payout=payout['id'], api_key=api_key, limit=1000)['data']
            fee_vals = defaultdict(float)
            for line in self.result_row_list:
                for fee in line['fee_details']:
                    fee_vals[fee['description']] += fee['amount']
            for description, amount in fee_vals.items():
                self.result_row_list.append({
                    'description': description,
                    'amount': -amount,
                    'created': payout['arrival_date'],
                    'type': 'fee',
                    })
            yield self.result_row_list

    def get_move_line_vals(self, line, *args, **kwargs):
        amount = line['amount']/100.
        vals = {
            'name': line['description'] or line.get('source'),
            'date_maturity': date.fromtimestamp(line['created']),
            'credit': amount > 0.0 and amount or 0.0,
            'debit': amount < 0.0 and -amount or 0.0,
            'transaction_ref': line.get('source'),
            'already_completed': False,
            'partner_id': None,
            'account_id': None,
            }
        if line['type'] == 'transfer':
            vals.update({
                'partner_id': self.journal.partner_id.id,
                'account_id': self.journal.default_debit_account_id.id,
                'already_completed': True,
                })
        elif line['type'] == 'fee':
            vals.update({
                'partner_id': self.journal.partner_id.id,
                'account_id': self.journal.commission_account_id.id,
                'already_completed': True,
                })
        return vals
