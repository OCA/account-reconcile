# -*- coding: utf-8 -*-
#
#
#    Author: Laurent Mignon
#    Copyright 2013 'ACSONE SA/NV'
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
#


from openerp import _, fields, models
from openerp.addons.account_statement_base_import.models.account_move \
    import ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.move.completion.rule"

    def _get_functions(self):
        res = super(AccountMoveCompletionRule, self)._get_functions()
        res.append(('get_from_bank_account',
                    'From bank account number (Normal or IBAN)'))
        return res

    def get_from_bank_account(self, line):
        """
        Match the partner based on the partner account number field
        Then, call the generic st_line method to complete other values.
        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
        """
        partner_acc_number = line.partner_acc_number
        if not partner_acc_number:
            return {}
        res = {}
        res_bank_obj = self.env['res.partner.bank']
        banks = res_bank_obj.search_by_acc_number(partner_acc_number)
        if len(banks) > 1:
            raise ErrorTooManyPartner(_('Line named "%s"  was matched '
                                        'by more than one partner for account '
                                        'number "%s".') %
                                      (line.name,
                                       partner_acc_number))
        if len(banks) == 1:
            partner = banks[0].partner_id
            res['partner_id'] = partner.id
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partner_acc_number = fields.Char(
        string='Account Number',
        size=64,
        help="Account number of the partner")
