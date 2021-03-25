# -*- coding: utf-8 -*-
# # Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMassReconcileMethod(models.Model):
    _inherit = 'account.mass.reconcile.method'

    def _get_all_rec_method(self):
        methods = super(AccountMassReconcileMethod, self)._get_all_rec_method()
        methods += [
            ('mass.reconcile.advanced.by.sale.line',
             'Advanced. Product, sale order line.'),
        ]
        return methods
