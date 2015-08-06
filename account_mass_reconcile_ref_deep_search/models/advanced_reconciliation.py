# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, models
from itertools import product


class MassReconciledAdvancedRefDeepSearch(models.TransientModel):

    _name = 'mass.reconcile.advanced.ref.deep.search'
    _inherit = 'mass.reconcile.advanced.ref'

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

        if value == opposite_value or \
                (key == 'ref' and value in opposite_value):
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
            if MassReconciledAdvancedRefDeepSearch._compare_values(
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
        return MassReconciledAdvancedRefDeepSearch.\
            _compare_matcher_values(mkey, mvalue, omvalue)
