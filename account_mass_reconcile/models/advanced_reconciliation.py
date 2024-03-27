# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MassReconcileAdvancedRef(models.TransientModel):
    _name = "mass.reconcile.advanced.ref"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile Advanced Ref"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("ref") and move_line.get("partner_id"))

    @staticmethod
    def _matchers(move_line):
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
        vs the opposite matchers, so you can gain performance by
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
        return (
            ("partner_id", move_line["partner_id"]),
            ("ref", (move_line["ref"] or "").lower().strip()),
        )

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
        yield ("partner_id", move_line["partner_id"])
        yield (
            "ref",
            (
                (move_line["ref"] or "").lower().strip(),
                (move_line["name"] or "").lower().strip(),
            ),
        )


class MassReconcileAdvancedName(models.TransientModel):
    _name = "mass.reconcile.advanced.name"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile Advanced Name"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("name", "/") != "/" and move_line.get("partner_id"))

    @staticmethod
    def _matchers(move_line):
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
        vs the opposite matchers, so you can gain performance by
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
        return (
            ("partner_id", move_line["partner_id"]),
            ("name", (move_line["name"] or "").lower().strip()),
        )

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
        yield ("partner_id", move_line["partner_id"])
        yield (
            "name",
            ((move_line["name"] or "").lower().strip(),),
        )
