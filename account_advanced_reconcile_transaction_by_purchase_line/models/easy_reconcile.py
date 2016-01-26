# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountEasyReconcileMethod(models.Model):

    _inherit = 'account.easy.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        methods = super(AccountEasyReconcileMethod, self).\
            _get_all_rec_method()
        methods += [
            ('easy.reconcile.advanced.by.purchase.line',
             'Advanced. GR/IR Key as partner, product, purchase order line.'),
        ]
        return methods
