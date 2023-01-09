# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from itertools import product

from odoo import api, models, registry
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class MassReconcileAdvanced(models.AbstractModel):
    _name = "mass.reconcile.advanced"
    _inherit = "mass.reconcile.base"
    _description = "Mass Reconcile Advanced"

    def _query_debit(self):
        """Select all move (debit>0) as candidate."""
        select = self._select_query()
        sql_from = self._from_query()
        where, params = self._where_query()
        where += " AND account_move_line.debit > 0 "
        where2, params2 = self._get_filter()
        query = " ".join((select, sql_from, where, where2))
        self.env.cr.execute(query, params + params2)
        return self.env.cr.dictfetchall()

    def _query_credit(self):
        """Select all move (credit>0) as candidate."""
        select = self._select_query()
        sql_from = self._from_query()
        where, params = self._where_query()
        where += " AND account_move_line.credit > 0 "
        where2, params2 = self._get_filter()
        query = " ".join((select, sql_from, where, where2))
        self.env.cr.execute(query, params + params2)
        return self.env.cr.dictfetchall()

    @staticmethod
    def _matchers(move_line):
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
            (They must be the same that `_opposite_matchers` returns,
            and their values to match in the opposite lines.
            A matching key can have multiples values.)
        """
        raise NotImplementedError

    @staticmethod
    def _opposite_matchers(move_line):
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
        An AND is used between the different keys.

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

    @classmethod
    def _compare_matcher_values(cls, key, values, opposite_values):
        """Compare every `values` from a matcher vs an opposite matcher
        and return True if it matches
        """
        for value, ovalue in product(values, opposite_values):
            # we do not need to compare all values, if one matches
            # we are done
            if cls._compare_values(key, value, ovalue):
                return True
        return False

    @staticmethod
    def _compare_matchers(matcher, opposite_matcher):
        """
        Prepare and check the matchers to compare
        """
        mkey, mvalue = matcher
        omkey, omvalue = opposite_matcher
        assert mkey == omkey, _(
            "A matcher %(mkey)s is compared with a matcher %(omkey)s, the _matchers and "
            "_opposite_matchers are probably wrong"
        ) % {"mkey": mkey, "omkey": omkey}
        if not isinstance(mvalue, (list, tuple)):
            mvalue = (mvalue,)
        if not isinstance(omvalue, (list, tuple)):
            omvalue = (omvalue,)
        return MassReconcileAdvanced._compare_matcher_values(mkey, mvalue, omvalue)

    def _compare_opposite(self, move_line, opposite_move_line, matchers):
        """Iterate over the matchers of the move lines vs opposite move lines
        and if they all match, return True.

        If all the matchers match for a move line and an opposite move line,
        they are candidate for a reconciliation.
        """
        opp_matchers = self._opposite_matchers(opposite_move_line)
        for matcher in matchers:
            try:
                opp_matcher = next(opp_matchers)
            except StopIteration as e:
                # if you fall here, you probably missed to put a `yield`
                # in `_opposite_matchers()`
                raise ValueError("Missing _opposite_matcher: %s" % matcher[0]) from e

            if not self._compare_matchers(matcher, opp_matcher):
                # if any of the matcher fails, the opposite line
                # is not a valid counterpart
                # directly returns so the next yield of _opposite_matchers
                # are not evaluated
                return False

        return True

    def _search_opposites(self, move_line, opposite_move_lines):
        """Search the opposite move lines for a move line

        :param dict move_line: the move line for which we search opposites
        :param list opposite_move_lines: list of dict of move lines values,
          the move lines we want to search for
        :return: list of matching lines
        """
        matchers = self._matchers(move_line)
        return [
            op
            for op in opposite_move_lines
            if self._compare_opposite(move_line, op, matchers)
        ]

    def _action_rec(self):
        self.flush()
        credit_lines = self._query_credit()
        debit_lines = self._query_debit()
        result = self._rec_auto_lines_advanced(credit_lines, debit_lines)
        return result

    def _skip_line(self, move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return False

    def _rec_group(self, reconcile_groups, lines_by_id):
        reconciled_ids = []
        for group_count, reconcile_group_ids in enumerate(reconcile_groups, start=1):

            _logger.debug(
                "Reconciling group %d/%d with ids %s",
                group_count,
                len(reconcile_groups),
                reconcile_group_ids,
            )
            group_lines = [lines_by_id[lid] for lid in reconcile_group_ids]
            reconciled, full = self._reconcile_lines(group_lines, allow_partial=True)
            if reconciled and full:
                reconciled_ids += reconcile_group_ids
        return reconciled_ids

    def _rec_group_by_chunk(self, reconcile_groups, lines_by_id, chunk_size):
        """Commit after each chunk

        :param list reconcile_groups: all groups to reconcile, will be split
        by chunk
        :param dict lines_by_id: dict of move lines values,
          the move lines we want to search for
        :return: list of reconciled lines
        """
        reconciled_ids = []

        _logger.info("Reconciling by chunk of %d", chunk_size)

        # Copy and commit current transient model before creating a new cursor
        # This is required to avoid CacheMiss when using data from `self`
        # which is created during current transaction.
        with registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            self_env = self.with_env(new_env)
            rec = self_env.create(self.copy_data())
        for i in range(0, len(reconcile_groups), chunk_size):
            chunk = reconcile_groups[i : i + chunk_size]
            _logger.debug("Reconcile group chunk %s", chunk)
            try:
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    # Re-use the committed transient we just committed
                    self_env = self.with_env(new_env).browse(rec.id)
                    reconciled_ids += self_env._rec_group(chunk, lines_by_id)
            except Exception as e:
                msg = "Reconciliation failed for group chunk %s with error:\n%s"
                _logger.exception(msg, chunk, e)
        return reconciled_ids

    def _rec_auto_lines_advanced(self, credit_lines, debit_lines):
        """Advanced reconciliation main loop"""
        # pylint: disable=invalid-commit
        reconciled_ids = []
        for rec in self:
            commit_every = rec.account_id.company_id.reconciliation_commit_every
            reconcile_groups = []
            _logger.info("%d credit lines to reconcile", len(credit_lines))
            for idx, credit_line in enumerate(credit_lines, start=1):
                if idx % 50 == 0:
                    _logger.info(
                        "... %d/%d credit lines inspected ...", idx, len(credit_lines)
                    )
                if self._skip_line(credit_line):
                    continue
                opposite_lines = self._search_opposites(credit_line, debit_lines)
                if not opposite_lines:
                    continue
                opposite_ids = [opp["id"] for opp in opposite_lines]
                line_ids = opposite_ids + [credit_line["id"]]
                for group in reconcile_groups:
                    if any([lid in group for lid in opposite_ids]):
                        _logger.debug(
                            "New lines %s matched with an existing " "group %s",
                            line_ids,
                            group,
                        )
                        group.update(line_ids)
                        break
                else:
                    _logger.debug("New group of lines matched %s", line_ids)
                    reconcile_groups.append(set(line_ids))
            lines_by_id = {line["id"]: line for line in credit_lines + debit_lines}
            _logger.info("Found %d groups to reconcile", len(reconcile_groups))
            if commit_every:
                reconciled_ids = self._rec_group_by_chunk(
                    reconcile_groups, lines_by_id, commit_every
                )
            else:
                reconciled_ids = self._rec_group(reconcile_groups, lines_by_id)
            _logger.info("Reconciliation is over")
        return reconciled_ids
