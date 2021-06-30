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

    def rec_auto_lines_three_way_matching(self, lines):
        three_way_limit = self._context.get('three_way_limit',0)
        skip_check = False
        if three_way_limit <= 0:
            skip_check = True
        non_rec_entry = self._context.get('non_rec_entry',0)
        reset_non_rec_entry = False
        if self._key_field is None:
            raise ValueError("_key_field has to be defined")
        debit_count = 0
        count = 0
        res = []
        debit_lsts = []
        credit_lsts = []
        for lin in lines:
            if not skip_check and lin.get('debit') and non_rec_entry>0:
                non_rec_entry-=1
            if lin.get('debit') > 0 and (skip_check or (three_way_limit > 0 and non_rec_entry <= 0)):
                if not skip_check:
                    three_way_limit-=1
                debit_lsts.append(lin)
            elif lin.get('credit') > 0:
                credit_lsts.append(lin)
        if len(debit_lsts) < self._context.get('three_way_limit',0):
            reset_non_rec_entry = True
        while debit_lsts:
            breaker = False
            for i in range(0, len(credit_lsts)):
                count = i + 1
                for j in range(count, len(credit_lsts)):
#                     print ("i - "+str(i) + "  j - " + str(j)+ "  Debit ID  " + str(debit_lsts[0].get('id')) + "   Credit ID  i - "+ str(credit_lsts[i].get('id')) + " : j - " + str(credit_lsts[j].get('id')) +"  ***Debit   " + str(round(debit_lsts[0].get('debit'), 2)) + "   ***Credit   " + str(round(credit_lsts[i].get('credit') + credit_lsts[j].get('credit'), 2)) + "      credit_lsts[i].get('credit')     " + str(round(credit_lsts[i].get('credit'), 2)) + "       credit_lsts[j].get('credit')     " + str(round(credit_lsts[j].get('credit'), 2)))
                    if self._key_field == 'product_partner' and round(debit_lsts[0].get('debit'), 2) == round(credit_lsts[i].get('credit') + credit_lsts[j].get('credit'), 2) and abs(debit_lsts[0].get('quantity')) == abs(credit_lsts[i].get('quantity')) + abs(credit_lsts[j].get('quantity')) and\
                        debit_lsts[0].get('product_id') == credit_lsts[i].get('product_id') == credit_lsts[j].get('product_id') and\
                        debit_lsts[0].get('partner_id') == credit_lsts[i].get('partner_id') == credit_lsts[j].get('partner_id'):
                            reconciled, dummy = self._reconcile_lines(
                                [debit_lsts[0], credit_lsts[i], credit_lsts[j]], allow_partial=False
                            )
                            if reconciled:
                                res += [debit_lsts[0]["id"], credit_lsts[i]["id"], credit_lsts[j]["id"]]
                                breaker = True
                                debit_count+=1
                                del credit_lsts[j]
                                del credit_lsts[i]
                                break
                    count += 1
                    if count > len(credit_lsts):
                        break
                if breaker:
                    break
            del debit_lsts[0]
        non_rec_entry = 0 if reset_non_rec_entry or skip_check else self._context.get('three_way_limit',0) + self._context.get('non_rec_entry',0) - debit_count
        self._context.get('rec_id').non_rec_entry = non_rec_entry
        return res

    def rec_auto_lines_simple(self, lines):
        if self._key_field is None:
            raise ValueError("_key_field has to be defined")
        count = 0
        res = []
        while count < len(lines):
            for i in range(count + 1, len(lines)):
#                 if lines[count][self._key_field] != lines[i][self._key_field]:
                if (self._key_field == 'product_partner' and (lines[count]['product_id'] != lines[i]['product_id'] or lines[count]['partner_id'] != lines[i]['partner_id'] or abs(lines[count]['quantity']) != abs(lines[i]['quantity']))) or (self._key_field != 'product_partner' and lines[count][self._key_field] != lines[i][self._key_field]):
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
#         return "ORDER BY account_move_line.%s" % self._key_field
        if self._key_field == 'product_partner':
            key_field = ('quantity','product_id','partner_id')
            return "ORDER BY abs(account_move_line.%s), account_move_line.%s, account_move_line.%s" % key_field
        else:
            key_field = self._key_field
            return "ORDER BY account_move_line.%s" % key_field

    def _action_rec(self):
        """Match only 2 move lines, do not allow partial reconcile"""

        key_field = self._key_field != 'product_partner' and self._key_field or 'product_id'
        key_field2 = self._key_field != 'product_partner' and False or 'partner_id'

        select = self._select_query()
        select += ", account_move_line.%s " % key_field
        if key_field2:
            select += ", account_move_line.%s " % key_field2
        where, params = self._where_query()
        where += " AND account_move_line.%s IS NOT NULL " % key_field
        if key_field2:
            where += " AND account_move_line.%s IS NOT NULL " % key_field2

        where2, params2 = self._get_filter()
        query = " ".join(
            (select, self._from_query(), where, where2, self._simple_order())
        )
        self.flush()
        self.env.cr.execute(query, params + params2)
        lines = self.env.cr.dictfetchall()
        if self._context.get('matching_type', False) == 'three_way':
            return self.rec_auto_lines_three_way_matching(lines)
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

class MassReconcileSimpleNamePartner(models.TransientModel):
    _name = "mass.reconcile.simple.product.partner"
    _inherit = "mass.reconcile.simple"
    _description = "Mass Reconcile Simple Product Partner"

    # has to be subclassed
    # field name used as key for matching the move lines
    _key_field = 'product_partner'

