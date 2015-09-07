# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012-2013, 2015 Camptocamp SA (Guewen Baconnier, Damien Crier)
#    Copyright (C) 2010   Sébastien Beau
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

# from openerp.osv.orm import AbstractModel, TransientModel
from openerp import models, api


class EasyReconcileSimple(models.AbstractModel):
    _name = 'easy.reconcile.simple'
    _inherit = 'easy.reconcile.base'

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = None

    @api.multi
    def rec_auto_lines_simple(self, lines):
        if self._key_field is None:
            raise ValueError("_key_field has to be defined")
        count = 0
        res = []
        while (count < len(lines)):
            for i in xrange(count + 1, len(lines)):
                if lines[count][self._key_field] != lines[i][self._key_field]:
                    break
                check = False
                if lines[count]['credit'] > 0 and lines[i]['debit'] > 0:
                    credit_line = lines[count]
                    debit_line = lines[i]
                    check = True
                elif lines[i]['credit'] > 0 and lines[count]['debit'] > 0:
                    credit_line = lines[i]
                    debit_line = lines[count]
                    check = True
                if not check:
                    continue
                reconciled, dummy = self._reconcile_lines(
                    [credit_line, debit_line],
                    allow_partial=False
                    )
                if reconciled:
                    res += [credit_line['id'], debit_line['id']]
                    del lines[i]
                    break
            count += 1
        return res, []  # empty list for partial, only full rec in "simple" rec

    @api.multi
    def _simple_order(self, *args, **kwargs):
        return "ORDER BY account_move_line.%s" % self._key_field

    def _action_rec(self):
        """Match only 2 move lines, do not allow partial reconcile"""
        select = self._select()
        select += ", account_move_line.%s " % self._key_field
        where, params = self._where()
        where += " AND account_move_line.%s IS NOT NULL " % self._key_field

        where2, params2 = self._get_filter()
        query = ' '.join((
            select,
            self._from(),
            where, where2,
            self._simple_order()))

        self.env.cr.execute(query, params + params2)
        lines = self.env.cr.dictfetchall()
        return self.rec_auto_lines_simple(lines)


class EasyReconcileSimpleName(models.TransientModel):
    _name = 'easy.reconcile.simple.name'
    _inherit = 'easy.reconcile.simple'

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = 'name'


class EasyReconcileSimplePartner(models.TransientModel):
    _name = 'easy.reconcile.simple.partner'
    _inherit = 'easy.reconcile.simple'

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = 'partner_id'


class EasyReconcileSimpleReference(models.TransientModel):
    _name = 'easy.reconcile.simple.reference'
    _inherit = 'easy.reconcile.simple'

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = 'ref'
