# -*- coding: utf-8 -*-
# © 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import re
from odoo import api, fields, models

ORDER_BY_PATTERN = r"ORDER BY"


class MassReconcileOptions(models.AbstractModel):
    _inherit = 'mass.reconcile.options'

    date_to = fields.Date(string='Date To')


class AccountMassReconcileMethod(models.Model):
    _inherit = 'account.mass.reconcile.method'

    @api.multi
    def _get_filter(self):
        """Order move lines by date for chronological processing"""
        where, params = super(AccountMassReconcileMethod, self)._get_filter()
        if self.date_to:
            date_to = self.date_to.strftime('%Y-%m-%d')
            if re.match(ORDER_BY_PATTERN, where):
                where = re.sub(ORDER_BY_PATTERN,
                               "AND date <= %s ORDER BY" % date_to, where)
            else:
                where = "%s AND date <= %s" % (where, date_to)
        return where, params
