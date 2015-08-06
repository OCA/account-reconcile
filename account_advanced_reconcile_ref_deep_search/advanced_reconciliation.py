# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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
from itertools import product
from openerp.tools.translate import _


class easy_reconcile_advanced_ref_deep_search(orm.TransientModel):

    _name = 'easy.reconcile.advanced.ref.deep.search'
    _inherit = 'easy.reconcile.advanced.ref'

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
            if easy_reconcile_advanced_ref_deep_search._compare_values(
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
        return easy_reconcile_advanced_ref_deep_search.\
            _compare_matcher_values(mkey, mvalue, omvalue)
