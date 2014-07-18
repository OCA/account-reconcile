# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich. Copyright Camptocamp SA
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


class easy_reconcile_advanced_bank_statement(orm.TransientModel):

    _name = 'easy.reconcile.advanced.bank_statement'
    _inherit = 'easy.reconcile.advanced'

    def _base_columns(self, rec):
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = super(easy_reconcile_advanced_bank_statement, self).\
            _base_columns(rec)
        aml_cols += ['account_move_line.statement_id',
                     'account_bank_statement.name as statement_name',
                     ]
        return aml_cols

    def _from(self, rec, *args, **kwargs):
        result = super(easy_reconcile_advanced_bank_statement, self).\
            _from(rec, *args, **kwargs)
        result = result + (
            " INNER JOIN account_bank_statement "
            "ON account_bank_statement.id = account_move_line.statement_id "
        )
        return result

    def _skip_line(self, cr, uid, rec, move_line, context=None):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        result = super(easy_reconcile_advanced_bank_statement, self).\
            _skip_line(cr, uid, rec, move_line, context=context)
        if result:
            return result
        return not (move_line.get('ref') and
                    move_line.get('partner_id'))

    def _matchers(self, cr, uid, rec, move_line, context=None):
        return (('partner_id', move_line['partner_id']),
                ('ref', move_line['ref'].lower().strip()))

    def _opposite_matchers(self, cr, uid, rec, move_line, context=None):
        yield ('partner_id', move_line['partner_id'])
        yield ('ref',
               (move_line['statement_name'] or '').lower().strip())

    # Re-defined for this particular rule; since the commission line is a
    # credit line inside of the target statement, it should also be considered
    # as an opposite to be reconciled.
    def _action_rec(self, cr, uid, rec, context=None):
        credit_lines = self._query_credit(cr, uid, rec, context=context)
        debit_lines = self._query_debit(cr, uid, rec, context=context)
        return self._rec_auto_lines_advanced(
                cr, uid, rec, credit_lines, credit_lines + debit_lines,
                context=context)
