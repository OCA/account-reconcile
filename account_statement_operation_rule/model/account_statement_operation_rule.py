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
        selection=[('balance', 'Balance'),
                   ('currency', 'Currencies')],
        string='Type',
        default='balance',
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
    sequence = fields.Integer(
        default=20,
        help="If several rules match, the first one is used.",
    )

    @api.multi
    def _is_valid_balance(self, statement_line, move_lines, balance):
        # TODO use float compare
        return self.amount_min <= balance <= self.amount_max

    @api.multi
    def _is_valid_multicurrency(self, statement_line, move_lines, balance):
        # FIXME: surely wrong
        if statement_line.currency_id == statement_line.company_id.currency_id:
            # not multicurrency
            return False
        amount_currency = statement_line.amount_currency
        for move_line in move_lines:
            if move_line.currency_id != statement_line.currency_id:
                # use case not supported, no rule found
                return self.browse()
            amount_currency -= move_line.amount_currency

        # amount in currency is the same, so the balance is
        # a difference due to currency rates
        if statement_line.currency_id.is_zero(amount_currency):
            return self._is_valid_balance(statement_line, move_lines, balance)
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
        if self.rule_type == 'balance':
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
        # TODO use is_zero
        if not balance:
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
