# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        if self._context is None:
            self._context = {}
        if self._context.get('only_partner_id'):
            args.append(('partner_id', '=', self._context['only_partner_id']))
        res = super(SaleOrder, self)._search(
            args,
            offset=offset, limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid)
        return res
