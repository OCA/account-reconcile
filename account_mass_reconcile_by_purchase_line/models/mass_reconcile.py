# -*- coding: utf-8 -*-
# © 2015-17 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountMassReconcileMethod(models.Model):
    _inherit = 'account.mass.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        methods = super(AccountMassReconcileMethod, self)._get_all_rec_method()
        methods += [
            ('mass.reconcile.advanced.by.purchase.line',
             'Advanced. Product, purchase order line.'),
        ]
        return methods
