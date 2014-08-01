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
from openerp.osv.orm import Model


class res_partner_bank(Model):
    _inherit = 'res.partner.bank'

    def search_by_acc_number(self, cr, uid, acc_number, context=None):
        '''
        Try to find the Account Number using a 'like' operator to avoid
        problems with the input mask used to store the value.
        '''
        # first try with an exact match
        ids = self.search(cr,
                          uid,
                          [('acc_number', '=', acc_number)],
                          context=context)
        if ids:
            return ids

        cr.execute("""
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
        return self.search(cr, uid,
                           [('id', 'in', [r[0] for r in cr.fetchall()])],
                           context=context)
