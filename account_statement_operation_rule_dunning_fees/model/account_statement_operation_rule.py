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

from openerp import models, fields, api, exceptions, _


class AccountStatementOperationRule(models.Model):
    _inherit = 'account.statement.operation.rule'

    rule_type = fields.Selection(
        selection_add=[('dunning_fees', 'Dunning Fees')],
    )

    @api.multi
    def _is_valid_dunning_fees(self, statement_line, move_lines, balance):
        control_line_obj = self.env['credit.control.line']
        control_lines = None
        for line in move_lines:
            domain = [('move_line_id', '=', line.id),
                      ('state', '=', 'sent')]
            line_control_lines = control_line_obj.search(domain)
            if line_control_lines and control_lines:
                # Several lines have credit control lines, use case
                # not covered, needs to be handled manually, dunning
                # fees rules not applied
                control_lines = None
                break
            elif line_control_lines:
                control_lines = line_control_lines
        if control_lines:
            # If we have an amount of 100.- with  3 credit control
            # lines, with the following fees amounts:
            # * 1st level: 5.-
            # * 2nd level: 10.-
            # * 3rd level: 15.-
            # The customer might pay from 100.- to 115.-, the rest
            # goes to the writeoff account configured on the operation.
            max_fees = max(control_lines.mapped('dunning_fees_amount'))
            # only use the dunning rule if the balance is between -fees and 0
            currency = statement_line.currency_for_rules()
            return self._between_with_bounds(0, balance, max_fees, currency)
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
        if self.rule_type == 'dunning_fees':
            return self._is_valid_dunning_fees(statement_line,
                                               move_lines,
                                               balance)
        else:
            _super = super(AccountStatementOperationRule, self)
            return _super.is_valid(statement_line, move_lines, balance)

    @api.constrains('sequence')
    def check_dunning_before_rounding(self):
        if self.rule_type == 'dunning_fees':
            operator = '<='
            other_type = 'rounding'
        elif self.rule_type == 'rounding':
            operator = '>'
            other_type = 'dunning_fees'
        else:
            return
        message = _('The Dunning Fees rule must be before the Rounding Rules')
        if self.search([('sequence', operator, self.sequence),
                        ('rule_type', '=', other_type)], limit=1):
            raise exceptions.ValidationError(message)
