# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class AccountStatementOperationRule(models.Model):
    _name = 'account.statement.operation.rule'

    _order = 'sequence ASC, id ASC'

    name = fields.Char()
    rule_type = fields.Selection(
        selection=[('rounding', 'Roundings'),
                   ('currency', 'Currencies')],
        string='Type',
        default='rounding',
        required=True,
    )
    operations = fields.Many2many(
        comodel_name='account.statement.operation.template',
        relation='account_statement_oper_rule_rel',
    )
    amount_min = fields.Float(
        string='Min. Amount',
        digits=dp.get_precision('Account'),
    )
    amount_max = fields.Float(
        string='Max. Amount',
        digits=dp.get_precision('Account'),
    )
    currencies = fields.Many2many(
        comodel_name='res.currency',
        string='Currencies',
        help="For 'Currencies' rules, you can choose for which currencies "
             "the rule will be applicable.",
    )
    sequence = fields.Integer(
        default=20,
        help="If several rules match, the first one is used.",
    )

    @staticmethod
    def _between_with_bounds(low, value, high, currency):
        """ Equivalent to a three way comparison: ``min <= value <= high``

        The comparisons are done with the currency to use the correct
        precision.
        """
        if currency.compare_amounts(value, low) == -1:
            return False
        if currency.compare_amounts(value, high) == 1:
            return False
        return True

    @api.multi
    def _balance_in_range(self, balance, currency):
        amount_min = self.amount_min
        amount_max = self.amount_max
        return self._between_with_bounds(amount_min, balance,
                                         amount_max, currency)

    @api.model
    def _is_multicurrency(self, statement_line):
        currency = statement_line.currency_for_rules()
        company_currency = statement_line.company_id.currency_id
        return currency != company_currency

    @api.multi
    def _is_valid_balance(self, statement_line, move_lines, balance):
        if self._is_multicurrency(statement_line):
            return False
        currency = statement_line.currency_for_rules()
        return self._balance_in_range(balance, currency)

    @api.multi
    def _is_valid_multicurrency(self, statement_line, move_lines, balance):
        """ Check if the multi-currency rule can be applied

        The rule is applied if and only if:
        * The currency is not company's one
        * The currency of the statement line and all the lines is the same
        * The balance of the amount currencies is 0
        * The balance is between the bounds configured on the rule
        """
        if not self._is_multicurrency(statement_line):
            return False
        currency = statement_line.currency_for_rules()
        if currency not in self.currencies:
            return False
        amount_currency = statement_line.amount_currency
        for move_line in move_lines:
            if move_line.currency_id != statement_line.currency_id:
                # use case not supported, no rule found
                return False
            amount_currency -= move_line.amount_currency

        # amount in currency is the same, so the balance is
        # a difference due to currency rates
        if statement_line.currency_id.is_zero(amount_currency):
            return self._balance_in_range(balance, currency)
        return False

    @api.multi
    def is_valid(self, statement_line, move_lines, balance):
        """ Returns True if a rule applies to a group of statement_line +
        move lines.

        This is the public method where the rule is evaluated whatever
        its type is.  When a rule returns True, it means that it is a
        candidate for the current reconciliation. The rule with the lowest
        number in the ``sequence`` field is chosen.

        :param statement_line: the line to reconcile
        :param move_lines: the selected move lines for reconciliation
        :param balance: the balance between the statement_line and the
                        move_lines. It could be computed here but it is
                        computed before to avoid to compute it for each
                        rule when called on multiple rules.
        """
        self.ensure_one()
        if self.rule_type == 'rounding':
            return self._is_valid_balance(statement_line, move_lines, balance)
        elif self.rule_type == 'currency':
            return self._is_valid_multicurrency(statement_line,
                                                move_lines,
                                                balance)

    @api.model
    def find_first_rule(self, statement_line, move_lines):
        """ Find the rules that apply to a statement line and
        a selection of move lines.

        :param statement_line: the line to reconcile
        :param move_lines: the selected move lines for reconciliation
        """
        balance = statement_line.amount
        for move_line in move_lines:
            balance += move_line.credit - move_line.debit

        currency = statement_line.currency_for_rules()
        if currency.is_zero(balance):
            return self.browse()

        rules = self.search([])
        # return the first applicable rule
        for rule in rules:
            if rule.is_valid(statement_line, move_lines, balance):
                return rule
        return self.browse()

    @api.model
    @api.returns('account.statement.operation.template')
    def operations_for_reconciliation(self, statement_line_id, move_line_ids):
        """ Find the rule for the current reconciliation and returns the
        ``account.statement.operation.template`` of the found rule.

        Called from the javascript reconciliation view.

        """
        line_obj = self.env['account.bank.statement.line']
        move_line_obj = self.env['account.move.line']
        statement_line = line_obj.browse(statement_line_id)
        move_lines = move_line_obj.browse(move_line_ids)
        rules = self.find_first_rule(statement_line, move_lines)
        return rules.operations
