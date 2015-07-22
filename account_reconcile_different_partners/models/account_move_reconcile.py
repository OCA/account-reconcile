# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    @api.multi
    def _check_same_partner(self):
        group = self.env.ref('account_reconcile_different_partners.'
                             'group_reconcile_different_partners')
        if group in self.env.user.groups_id:
            return True
        return super(AccountMoveReconcile, self)._check_same_partner()

    def _register_hook(self, cr):
        for i in range(len(self._constraints)):
            func, message, fields = self._constraints[i]
            if func.__name__ == '_check_same_partner' and\
                    func != self._check_same_partner.__func__:
                self._constraints[i] = (self._check_same_partner.__func__,
                                        message, fields)
        return super(AccountMoveReconcile, self)._register_hook(cr)
