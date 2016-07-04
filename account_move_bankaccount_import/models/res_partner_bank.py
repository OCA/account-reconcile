# -*- coding: utf-8 -*-
# © 2013 ACSONE SA/NV
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
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
