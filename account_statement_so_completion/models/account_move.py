# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Joel Grand-Guillaume                                              #
#   Copyright 2011-2012 Camptocamp SA                                         #
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp import _, models
from openerp.addons.account_statement_base_import.models.account_move \
    import ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):

    _name = "account.move.completion.rule"
    _inherit = "account.move.completion.rule"

    def _get_functions(self):
        res = super(AccountMoveCompletionRule, self)._get_functions()
        res.append(
            ('get_from_name_and_so', 'From line name (based on SO number)')
        )
        return res

    # Should be private but data are initialised with no update XML
    def get_from_name_and_so(self, line):
        """
        Match the partner based on the SO number and the reference of the
        statement line. Then, call the generic get_values_for_line method to
        complete other values. If more than one partner matched, raise the
        ErrorTooManyPartner error.

        :param int/long st_line: read of the concerned
        account.bank.statement.line

        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
        """
        res = {}
        so_obj = self.env['sale.order']
        orders = so_obj.search([('name', '=', line.name)])
        if len(orders) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s"  was matched by more '
                  'than one partner while looking on SO by ref.') %
                line.name)
        if len(orders) == 1:
            res['partner_id'] = orders[0].partner_id.id
        return res
