# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountEasyReconcileMethod(models.Model):

    _inherit = 'account.easy.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        methods = super(AccountEasyReconcileMethod, self).\
            _get_all_rec_method()
        methods += [
            ('easy.reconcile.advanced.ref',
             'Advanced. Partner and Ref.'),
        ]
        return methods
