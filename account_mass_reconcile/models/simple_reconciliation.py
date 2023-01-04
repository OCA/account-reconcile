# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MassReconcileSimple(models.AbstractModel):
    _name = "mass.reconcile.simple"
    _inherit = "mass.reconcile.base"
    _description = "Mass Reconcile Simple"

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = None

    def rec_auto_lines_simple(self, lines):
        if self._key_field is None:
            raise ValueError("_key_field has to be defined")
        count = 0
        res = []
        while count < len(lines):
            for i in range(count + 1, len(lines)):
                if lines[count][self._key_field] != lines[i][self._key_field]:
                    break
                check = False
                if lines[count]["credit"] > 0 and lines[i]["debit"] > 0:
                    credit_line = lines[count]
                    debit_line = lines[i]
                    check = True
                elif lines[i]["credit"] > 0 and lines[count]["debit"] > 0:
                    credit_line = lines[i]
                    debit_line = lines[count]
                    check = True
                if not check:
                    continue
                reconciled, dummy = self._reconcile_lines(
                    [credit_line, debit_line], allow_partial=False
                )
                if reconciled:
                    res += [credit_line["id"], debit_line["id"]]
                    del lines[i]
                    if (
                        self.env.context.get("commit_every", 0)
                        and len(res) % self.env.context["commit_every"] == 0
                    ):
                        # new cursor is already open in cron
                        self.env.cr.commit()  # pylint: disable=invalid-commit
                        _logger.info(
                            "Commit the reconciliations after %d groups", len(res)
                        )
                    break
            count += 1
        return res

    def _simple_order(self, *args, **kwargs):
        return "ORDER BY account_move_line.%s" % self._key_field

    def _action_rec(self):
        """Match only 2 move lines, do not allow partial reconcile"""
        select = self._select_query()
        select += ", account_move_line.%s " % self._key_field
        where, params = self._where_query()
        where += " AND account_move_line.%s IS NOT NULL " % self._key_field

        where2, params2 = self._get_filter()
        query = " ".join(
            (select, self._from_query(), where, where2, self._simple_order())
        )
        self.env.flush_all()
        self.env.cr.execute(query, params + params2)
        lines = self.env.cr.dictfetchall()
        return self.rec_auto_lines_simple(lines)


class MassReconcileSimpleName(models.TransientModel):
    _name = "mass.reconcile.simple.name"
    _inherit = "mass.reconcile.simple"
    _description = "Mass Reconcile Simple Name"

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = "name"


class MassReconcileSimplePartner(models.TransientModel):
    _name = "mass.reconcile.simple.partner"
    _inherit = "mass.reconcile.simple"
    _description = "Mass Reconcile Simple Partner"

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = "partner_id"


class MassReconcileSimpleReference(models.TransientModel):
    _name = "mass.reconcile.simple.reference"
    _inherit = "mass.reconcile.simple"
    _description = "Mass Reconcile Simple Reference"

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = "ref"
