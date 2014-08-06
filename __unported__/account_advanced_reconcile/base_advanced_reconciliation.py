# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Contributor: Leonardo Pistone
#    Copyright 2012-2014 Camptocamp SA
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
import logging

from itertools import product
from openerp.osv import orm
from openerp import pooler
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class easy_reconcile_advanced(orm.AbstractModel):
    _name = 'easy.reconcile.advanced'
    _inherit = 'easy.reconcile.base'

    def _query_debit(self, cr, uid, rec, context=None):
        """Select all move (debit>0) as candidate. """
        select = self._select(rec)
        sql_from = self._from(rec)
        where, params = self._where(rec)
        where += " AND account_move_line.debit > 0 "
        where2, params2 = self._get_filter(cr, uid, rec, context=context)
        query = ' '.join((select, sql_from, where, where2))
        cr.execute(query, params + params2)
        return cr.dictfetchall()

    def _query_credit(self, cr, uid, rec, context=None):
        """Select all move (credit>0) as candidate. """
        select = self._select(rec)
        sql_from = self._from(rec)
        where, params = self._where(rec)
        where += " AND account_move_line.credit > 0 "
        where2, params2 = self._get_filter(cr, uid, rec, context=context)
        query = ' '.join((select, sql_from, where, where2))
        cr.execute(query, params + params2)
        return cr.dictfetchall()

    def _matchers(self, cr, uid, rec, move_line, context=None):
        """
        Return the values used as matchers to find the opposite lines

        All the matcher keys in the dict must have their equivalent in
        the `_opposite_matchers`.

        The values of each matcher key will be searched in the
        one returned by the `_opposite_matchers`

        Must be inherited to implement the matchers for one method

        As instance, it can return:
        return ('ref', move_line['rec'])

        or
        return (('partner_id', move_line['partner_id']),
                ('ref', "prefix_%s" % move_line['rec']))

        All the matchers have to be found in the opposite lines
        to consider them as "opposite"

        The matchers will be evaluated in the same order as declared
        vs the the opposite matchers, so you can gain performance by
        declaring first the partners with the less computation.

        All matchers should match with their opposite to be considered
        as "matching".
        So with the previous example, partner_id and ref have to be
        equals on the opposite line matchers.

        :return: tuple of tuples (key, value) where the keys are
            the matchers keys
            (must be the same than `_opposite_matchers` returns,
            and their values to match in the opposite lines.
            A matching key can have multiples values.
        """
        raise NotImplementedError

    def _opposite_matchers(self, cr, uid, rec, move_line, context=None):
        """
        Return the values of the opposite line used as matchers
        so the line is matched

        Must be inherited to implement the matchers for one method
        It can be inherited to apply some formatting of fields
        (strip(), lower() and so on)

        This method is the counterpart of the `_matchers()` method.

        Each matcher has to yield its value respecting the order
        of the `_matchers()`.

        When a matcher does not correspond, the next matchers won't
        be evaluated so the ones which need the less computation
        have to be executed first.

        If the `_matchers()` returns:
        (('partner_id', move_line['partner_id']),
         ('ref', move_line['ref']))

        Here, you should yield :
        yield ('partner_id', move_line['partner_id'])
        yield ('ref', move_line['ref'])

        Note that a matcher can contain multiple values, as instance,
        if for a move line, you want to search from its `ref` in the
        `ref` or `name` fields of the opposite move lines, you have to
        yield ('partner_id', move_line['partner_id'])
        yield ('ref', (move_line['ref'], move_line['name'])

        An OR is used between the values for the same key.
        An AND is used between the differents keys.

        :param dict move_line: values of the move_line
        :yield: matchers as tuple ('matcher key', value(s))
        """
        raise NotImplementedError

    @staticmethod
    def _compare_values(key, value, opposite_value):
        """Can be inherited to modify the equality condition
        specifically according to the matcher key (maybe using
        a like operator instead of equality on 'ref' as instance)
        """
        # consider that empty vals are not valid matchers
        # it can still be inherited for some special cases
        # where it would be allowed
        if not (value and opposite_value):
            return False

        if value == opposite_value:
            return True
        return False

    @staticmethod
    def _compare_matcher_values(key, values, opposite_values):
        """ Compare every values from a matcher vs an opposite matcher
        and return True if it matches
        """
        for value, ovalue in product(values, opposite_values):
            # we do not need to compare all values, if one matches
            # we are done
            if easy_reconcile_advanced._compare_values(key, value, ovalue):
                return True
        return False

    @staticmethod
    def _compare_matchers(matcher, opposite_matcher):
        """
        Prepare and check the matchers to compare
        """
        mkey, mvalue = matcher
        omkey, omvalue = opposite_matcher
        assert mkey == omkey, \
            (_("A matcher %s is compared with a matcher %s, the _matchers and "
               "_opposite_matchers are probably wrong") % (mkey, omkey))
        if not isinstance(mvalue, (list, tuple)):
            mvalue = mvalue,
        if not isinstance(omvalue, (list, tuple)):
            omvalue = omvalue,
        return easy_reconcile_advanced._compare_matcher_values(mkey, mvalue,
                                                               omvalue)

    def _compare_opposite(self, cr, uid, rec, move_line, opposite_move_line,
                          matchers, context=None):
        """ Iterate over the matchers of the move lines vs opposite move lines
        and if they all match, return True.

        If all the matchers match for a move line and an opposite move line,
        they are candidate for a reconciliation.
        """
        opp_matchers = self._opposite_matchers(cr, uid, rec, opposite_move_line,
                                               context=context)
        for matcher in matchers:
            try:
                opp_matcher = opp_matchers.next()
            except StopIteration:
                # if you fall here, you probably missed to put a `yield`
                # in `_opposite_matchers()`
                raise ValueError("Missing _opposite_matcher: %s" % matcher[0])

            if not self._compare_matchers(matcher, opp_matcher):
                # if any of the matcher fails, the opposite line
                # is not a valid counterpart
                # directly returns so the next yield of _opposite_matchers
                # are not evaluated
                return False

        return True

    def _search_opposites(self, cr, uid, rec, move_line, opposite_move_lines,
                          context=None):
        """Search the opposite move lines for a move line

        :param dict move_line: the move line for which we search opposites
        :param list opposite_move_lines: list of dict of move lines values,
          the move lines we want to search for
        :return: list of matching lines
        """
        matchers = self._matchers(cr, uid, rec, move_line, context=context)
        return [op for op in opposite_move_lines if
                self._compare_opposite(
                    cr, uid, rec, move_line, op, matchers, context=context)]

    def _action_rec(self, cr, uid, rec, context=None):
        # we use a new cursor to be able to commit the reconciliation
        # often. We have to create it here and not later to avoid problems
        # where the new cursor sees the lines as reconciles but the old one
        # does not.
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['commit_every'] = (
            rec.journal_id.company_id.reconciliation_commit_every
        )
        if ctx['commit_every']:
            new_cr = pooler.get_db(cr.dbname).cursor()
        else:
            new_cr = cr
        try:
            credit_lines = self._query_credit(new_cr, uid, rec, context=ctx)
            debit_lines = self._query_debit(new_cr, uid, rec, context=ctx)
            result = self._rec_auto_lines_advanced(
                new_cr, uid, rec, credit_lines, debit_lines, context=ctx)
        finally:
            if ctx['commit_every']:
                new_cr.commit()
                new_cr.close()
        return result

    def _skip_line(self, cr, uid, rec, move_line, context=None):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return False

    def _rec_auto_lines_advanced(self, cr, uid, rec, credit_lines, debit_lines,
                                 context=None):
        """ Advanced reconciliation main loop """
        reconciled_ids = []
        partial_reconciled_ids = []
        reconcile_groups = []
        _logger.info("%d credit lines to reconcile", len(credit_lines))
        for idx, credit_line in enumerate(credit_lines, start=1):
            if idx % 50 == 0:
                _logger.info("... %d/%d credit lines inspected ...", idx,
                             len(credit_lines))
            if self._skip_line(cr, uid, rec, credit_line, context=context):
                continue
            opposite_lines = self._search_opposites(
                cr, uid, rec, credit_line, debit_lines, context=context)
            if not opposite_lines:
                continue
            opposite_ids = [l['id'] for l in opposite_lines]
            line_ids = opposite_ids + [credit_line['id']]
            for group in reconcile_groups:
                if any([lid in group for lid in opposite_ids]):
                    _logger.debug("New lines %s matched with an existing "
                                  "group %s", line_ids, group)
                    group.update(line_ids)
                    break
            else:
                _logger.debug("New group of lines matched %s", line_ids)
                reconcile_groups.append(set(line_ids))
        lines_by_id = dict([(l['id'], l) for l in credit_lines + debit_lines])
        _logger.info("Found %d groups to reconcile", len(reconcile_groups))
        for group_count, reconcile_group_ids in enumerate(reconcile_groups,
                                                          start=1):
            _logger.debug("Reconciling group %d/%d with ids %s",
                          group_count, len(reconcile_groups),
                          reconcile_group_ids)
            group_lines = [lines_by_id[lid] for lid in reconcile_group_ids]
            reconciled, full = self._reconcile_lines(
                cr, uid, rec, group_lines, allow_partial=True, context=context)
            if reconciled and full:
                reconciled_ids += reconcile_group_ids
            elif reconciled:
                partial_reconciled_ids += reconcile_group_ids

            if (context['commit_every'] and
                    group_count % context['commit_every'] == 0):
                cr.commit()
                _logger.info("Commit the reconciliations after %d groups",
                             group_count)
        _logger.info("Reconciliation is over")
        return reconciled_ids, partial_reconciled_ids
