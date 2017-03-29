# -*- coding: utf-8 -*-
# © 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, models, api
from itertools import product


class MassReconciledAdvancedPartnerAmount(models.TransientModel):

    _name = 'mass.reconcile.advanced.partner.amount'
    _inherit = 'mass.reconcile.advanced'

    @api.multi
    def _matchers(self, move_line):
        """
        Return the values used as matchers to find the opposite lines

        All the matcher keys in the dict must have their equivalent in
        the `_opposite_matchers`.

        The values of each matcher key will be searched in the
        one returned by the `_opposite_matchers`

        Must be inherited to implement the matchers for one method

        For instance, it can return:
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
        return (('partner_id', move_line['partner_id']),
                )

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
        yield ('partner_id', move_line['partner_id'])

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
            if MassReconciledAdvancedPartnerAmount._compare_values(
                    key, value, ovalue):
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
        return MassReconciledAdvancedPartnerAmount.\
            _compare_matcher_values(mkey, mvalue, omvalue)
