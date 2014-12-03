# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm


class account_bank_statement_line(orm.Model):

    _inherit = 'account.bank.statement.line'

    def _domain_move_lines_for_reconciliation(self, cr, uid, st_line,
                                              excluded_ids=None, str=False,
                                              additional_domain=None,
                                              context=None):
        _super = super(account_bank_statement_line, self)
        _get_domain = _super._domain_move_lines_for_reconciliation
        domain = _get_domain(cr, uid, st_line, excluded_ids=excluded_ids,
                             str=str, additional_domain=additional_domain,
                             context=context)
        if not str and str != '/':
            return domain
        domain = domain[:]
        domain.insert(-1, '|')
        domain.append(('transaction_ref', 'ilike', str))
        return domain

    def _domain_reconciliation_proposition(self, cr, uid, st_line,
                                           excluded_ids=None, context=None):
        _super = super(account_bank_statement_line, self)
        _get_domain = _super._domain_reconciliation_proposition
        domain = _get_domain(cr, uid, st_line, excluded_ids=excluded_ids,
                             context=context)
        new_domain = []
        for criterion in domain:
            if len(criterion) == 3:
                field, op, value = criterion
                if (field, op) == ('ref', '='):
                    new_domain += [
                        '|',
                        ('transaction_ref', '=', value),
                    ]
            new_domain.append(criterion)
        return new_domain
