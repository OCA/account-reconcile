# -*- coding: utf-8 -*-
# © 2012-2016 Camptocamp SA (Guewen Baconnier, Damien Crier, Matthieu Dietrich)
# © 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import models, api
from itertools import product
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class MassReconcileAdvanced(models.AbstractModel):
    _name = 'mass.reconcile.advanced'
    _inherit = 'mass.reconcile.base'

    @api.multi
    def _query_debit(self):
        """Select all move (debit>0) as candidate. """
        select = self._select()
        sql_from = self._from()
        where, params = self._where()
        where += " AND account_move_line.debit > 0 "
        where2, params2 = self._get_filter()
        query = ' '.join((select, sql_from, where, where2))
        self.env.cr.execute(query, params + params2)
        return self.env.cr.dictfetchall()

    def _query_credit(self):
        """Select all move (credit>0) as candidate. """
        select = self._select()
        sql_from = self._from()
        where, params = self._where()
        where += " AND account_move_line.credit > 0 "
        where2, params2 = self._get_filter()
        query = ' '.join((select, sql_from, where, where2))
        self.env.cr.execute(query, params + params2)
        return self.env.cr.dictfetchall()

    @api.multi
    def _matchers(self, move_line):
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

    @api.multi
    def _opposite_matchers(self, move_line):
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
            if MassReconcileAdvanced._compare_values(key, value, ovalue):
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
        return MassReconcileAdvanced._compare_matcher_values(mkey, mvalue,
                                                             omvalue)

    @api.multi
    def _compare_opposite(self, move_line, opposite_move_line, matchers):
        """ Iterate over the matchers of the move lines vs opposite move lines
        and if they all match, return True.

        If all the matchers match for a move line and an opposite move line,
        they are candidate for a reconciliation.
        """
        opp_matchers = self._opposite_matchers(opposite_move_line)
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

    @api.multi
    def _search_opposites(self, move_line, opposite_move_lines):
        """Search the opposite move lines for a move line

        :param dict move_line: the move line for which we search opposites
        :param list opposite_move_lines: list of dict of move lines values,
          the move lines we want to search for
        :return: list of matching lines
        """
        matchers = self._matchers(move_line)
        return [op for op in opposite_move_lines if
                self._compare_opposite(move_line, op, matchers)]

    def _action_rec(self):
        credit_lines = self._query_credit()
        debit_lines = self._query_debit()
        result = self._rec_auto_lines_advanced(credit_lines, debit_lines)
        return result

    @api.multi
    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return False

    @api.multi
    def _rec_auto_lines_advanced(self, credit_lines, debit_lines):
        """ Advanced reconciliation main loop """
        flow = ReconcileAdvancedFlow(self, credit_lines, debit_lines)
        return flow.run()


class ReconcileAdvancedFlow(object):

    def __init__(self, rule, credit_lines, debit_lines):
        self.rule = rule
        self.env = rule.env
        self.credit_lines = dict(
            [(l['id'], l) for l in credit_lines]
        )
        self.credit_lines_number = len(self.credit_lines)
        self.debit_lines = dict(
            [(l['id'], l) for l in debit_lines]
        )
        self.reconciled_ids = []
        # number of reconciled groups, used for the commit by batches
        self.group_count = 0

    def _get_lines_for_ids(self, line_ids):
        lines = []
        for line_id in line_ids:
            line = (self.debit_lines.get(line_id) or
                    self.credit_lines.get(line_id))
            assert line
            lines.append(line)
        return lines

    def _try_fast_path_reconcile(self, line_ids):
        """ Check if a group is complete so we can reconcile early

        A group is considered completed if it's balance is below the write-off.
        In that case we can reconcile it even if not all the lines
        have been checked. Also, we can remove the debit lines so they will be
        removed from all the future matchings.
        """
        lines = self._get_lines_for_ids(line_ids)
        below_writeoff, __ = self.rule._below_writeoff_limit(
            lines, self.rule.write_off
        )
        if below_writeoff:
            reconciled, full = self._reconcile(line_ids, lines)
            # only in the fast path, we get rid of the
            # used lines so we'll stop to compare them
            for line_id in line_ids:
                self.debit_lines.pop(line_id, None)
            return reconciled, full
        return False, False

    def _reconcile(self, line_ids, group_lines):
        _logger.debug("Reconciling group with ids %s", line_ids)
        reconciled, full = self.rule._reconcile_lines(
            group_lines, allow_partial=True
        )

        if reconciled:
            self.group_count += 1
        if reconciled and full:
            self.reconciled_ids += line_ids

        if (self.env.context.get('commit_every') and
                self.group_count %
                self.env.context['commit_every'] == 0):
            self.env.cr.commit()
            _logger.info("Commit the reconciliations after %d groups",
                         self.group_count)
        return reconciled, full

    def run(self):
        reconcile_groups = []

        _logger.info("%d credit lines to reconcile", self.credit_lines_number)
        for idx, credit_line in enumerate(self.credit_lines.itervalues(),
                                          start=1):
            if idx % 50 == 0:
                _logger.info("... %d/%d credit lines inspected, still have"
                             " %d candidate debit lines ...", idx,
                             self.credit_lines_number, len(self.debit_lines))
            if self.rule._skip_line(credit_line):
                continue
            opposite_lines = self.rule._search_opposites(
                credit_line,
                self.debit_lines.itervalues()
            )
            if not opposite_lines:
                continue
            opposite_ids = [l['id'] for l in opposite_lines]
            line_ids = opposite_ids + [credit_line['id']]
            for group in reconcile_groups:
                if any([lid in group for lid in opposite_ids]):
                    _logger.debug("New lines %s matched with an existing "
                                  "group %s", line_ids, group)
                    group.update(line_ids)
                    reconciled, __ = self._try_fast_path_reconcile(group)
                    if reconciled:
                        # safe to do so only because we stop the iteration
                        reconcile_groups.remove(group)
                    break
            else:
                _logger.debug("New group of lines matched %s", line_ids)
                reconciled, __ = self._try_fast_path_reconcile(line_ids)
                if not reconciled:
                    # group is not complete, we will maybe find another line
                    # later to complete it
                    reconcile_groups.append(set(line_ids))

        # remaining groups are probably partial reconciliations
        _logger.info("Still %d groups to reconcile",
                     len(reconcile_groups))
        for idx, reconcile_group_ids in enumerate(reconcile_groups, start=1):
            _logger.debug("Reconciling group %d/%d with ids %s",
                          idx, len(reconcile_groups), reconcile_group_ids)
            self._reconcile(reconcile_group_ids,
                            self._get_lines_for_ids(reconcile_group_ids)
                            )

        _logger.info("Reconciliation is over")
        return self.reconciled_ids
