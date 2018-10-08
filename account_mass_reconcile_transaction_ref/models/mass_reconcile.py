# Copyright 2013-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, models


class AccountMassReconcileMethod(models.Model):

    _inherit = 'account.mass.reconcile.method'

    @api.model
    def _get_all_rec_method(self):
        methods = super(AccountMassReconcileMethod, self)._get_all_rec_method()
        methods += [
            ('mass.reconcile.advanced.transaction_ref',
             'Advanced. Partner and Transaction Ref.'),
            ('mass.reconcile.advanced.trans_ref_vs_ref',
             'Advanced. Partner and Transaction Ref. vs Ref.'),
        ]
        return methods
