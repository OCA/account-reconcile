# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api


class AccountMassReconcileMethod(models.Model):
    _inherit = 'account.mass.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        res = super(AccountMassReconcileMethod, self)._get_all_rec_method()
        res.append((
            'mass.reconcile.advanced.partner',
            'Advanced. Partner'
        ))
        return res
