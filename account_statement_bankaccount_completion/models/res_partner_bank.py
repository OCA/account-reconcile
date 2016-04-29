#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import api, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.multi
    def search_by_acc_number(self, acc_number):
        '''
        Try to find the Account Number using a 'like' operator to avoid
        problems with the input mask used to store the value.
        '''
        # first try with an exact match
        banks = self.search([('acc_number', '=', acc_number)])
        if banks:
            return banks

        self.env.cr.execute("""
            SELECT
                id
            FROM
                res_partner_bank
            WHERE
                regexp_replace(acc_number,'([^[:alnum:]])', '','g')
                ilike
                regexp_replace(%s,'([^[:alnum:]])', '','g')
        """, (acc_number,))
        # apply security constraints by using the orm
        return self.search(
            [('id', 'in', [r[0] for r in self.env.cr.fetchall()])])
