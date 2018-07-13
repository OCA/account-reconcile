# © 2015-18 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMassReconcileMethod(models.Model):
    _inherit = 'account.mass.reconcile.method'

    @staticmethod
    def _get_reconcilation_methods():
        methods = super(
            AccountMassReconcileMethod, AccountMassReconcileMethod).\
            _get_reconcilation_methods()
        methods += [
            ('mass.reconcile.advanced.by.purchase.line',
             'Advanced. Product, purchase order line.'),
        ]
        return methods
