# -*- coding: utf-8 -*-
# © 2012-2014 Camptocamp SA - Guewen Baconnier

from openerp import models, api


class account_easy_reconcile_method(models.Model):

    _inherit = 'account.easy.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        methods = super(account_easy_reconcile_method, self).\
            _get_all_rec_method()
        methods += [
            ('easy.reconcile.advanced.ref',
             'Advanced. Partner and Ref.'),
        ]
        return methods
