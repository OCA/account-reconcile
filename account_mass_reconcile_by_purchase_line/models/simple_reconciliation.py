# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class MassReconcileAdvancedByPurchaseLineName(models.TransientModel):
    _name = 'mass.reconcile.advanced.by.purchase.line'
    _inherit = 'mass.reconcile.simple'

    _key_field = 'purchase_line_id'
