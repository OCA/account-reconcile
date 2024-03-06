# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from operator import itemgetter

from odoo import _, fields, models
from odoo.tools.safe_eval import safe_eval


class MassReconcileBase(models.AbstractModel):
    """Abstract Model for reconciliation methods"""

    _name = "mass.reconcile.base"
    _inherit = "mass.reconcile.options"
    _description = "Mass Reconcile Base"

    account_id = fields.Many2one("account.account", string="Account", required=True)
    partner_ids = fields.Many2many(
        comodel_name="res.partner", string="Restrict on partners"
    )
    # other fields are inherited from mass.reconcile.options

    def automatic_reconcile(self):
        """Reconciliation method called from the view.

        :return: list of reconciled ids
        """
        self.ensure_one()
        return self._action_rec()

    def _action_rec(self):
        """Must be inherited to implement the reconciliation

        :return: list of reconciled ids
        """
        raise NotImplementedError

    @staticmethod
    def _base_columns():
        """Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = (
            "id",
            "debit",
            "credit",
            "currency_id",
            "amount_residual",
            "amount_residual_currency",
            "date",
            "ref",
            "name",
            "partner_id",
            "account_id",
            "reconciled",
            "move_id",
        )
        return [f"account_move_line.{col}" for col in aml_cols]

    def _selection_columns(self):
        return self._base_columns()

    def _select_query(self, *args, **kwargs):
        return "SELECT %s" % ", ".join(self._selection_columns())

    def _from_query(self, *args, **kwargs):
        return "FROM account_move_line "

    def _where_query(self, *args, **kwargs):
        self.ensure_one()
        where = (
            "WHERE account_move_line.account_id = %s "
            "AND NOT account_move_line.reconciled "
            "AND parent_state = 'posted'"
        )
        # it would be great to use dict for params
        # but as we use _where_calc in _get_filter
        # which returns a list, we have to
        # accommodate with that
        params = [self.account_id.id]
        if self.partner_ids:
            where += " AND account_move_line.partner_id IN %s"
            params.append(tuple(line.id for line in self.partner_ids))
        return where, params

    def _get_filter(self):
        self.ensure_one()
        ml_obj = self.env["account.move.line"]
        where = ""
        params = []
        if self._filter:
            dummy, where, params = ml_obj._where_calc(safe_eval(self._filter)).get_sql()
            if where:
                where = " AND %s" % where
        return where, params

    def _below_writeoff_limit(self, lines, writeoff_limit):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Account")

        writeoff_amount = round(
            sum(line["amount_residual"] for line in lines), precision
        )
        writeoff_amount_curr = round(
            sum(line["amount_residual_currency"] for line in lines), precision
        )

        first_currency = lines[0]["currency_id"]
        if all([line["currency_id"] == first_currency for line in lines]):
            ref_amount = writeoff_amount_curr
            same_curr = True
            # TODO if currency != company currency compute writeoff_limit in currency
        else:
            ref_amount = writeoff_amount
            same_curr = False

        return (
            bool(writeoff_limit >= abs(ref_amount)),
            writeoff_amount,
            writeoff_amount_curr,
            same_curr,
        )

    def _get_rec_date(self, lines, based_on="end_period_last_credit"):
        self.ensure_one()

        def last_date(mlines):
            return max(mlines, key=itemgetter("date"))

        def oldest_date(mlines):
            return min(mlines, key=itemgetter("date"))

        def credit(mlines):
            return [line for line in mlines if line["credit"] > 0]

        def debit(mlines):
            return [line for line in mlines if line["debit"] > 0]

        if based_on == "newest":
            return last_date(lines)["date"]
        elif based_on == "oldest":
            return oldest_date(lines)["date"]
        elif based_on == "newest_credit":
            return last_date(credit(lines))["date"]
        elif based_on == "newest_debit":
            return last_date(debit(lines))["date"]
        # reconcilation date will be today
        # when date is None
        return None

    def create_write_off(self, lines, amount, amount_curr, same_curr):
        self.ensure_one()
        if amount < 0:
            account = self.account_profit_id
        else:
            account = self.account_lost_id
        currency = same_curr and lines[0].currency_id or lines[0].company_id.currency_id
        journal = self.journal_id
        partners = lines.mapped("partner_id")
        write_off_vals = {
            "name": _("Automatic writeoff"),
            "amount_currency": same_curr and amount_curr or amount,
            "debit": amount > 0.0 and amount or 0.0,
            "credit": amount < 0.0 and -amount or 0.0,
            "partner_id": len(partners) == 1 and partners.id or False,
            "account_id": account.id,
            "journal_id": journal.id,
            "currency_id": currency.id,
        }
        counterpart_account = lines.mapped("account_id")
        counter_part = write_off_vals.copy()
        counter_part["debit"] = write_off_vals["credit"]
        counter_part["credit"] = write_off_vals["debit"]
        counter_part["amount_currency"] = -write_off_vals["amount_currency"]
        counter_part["account_id"] = (counterpart_account.id,)

        move = self.env["account.move"].create(
            {
                "date": lines.env.context.get("date_p") or fields.Date.today(),
                "journal_id": journal.id,
                "currency_id": currency.id,
                "line_ids": [(0, 0, write_off_vals), (0, 0, counter_part)],
            }
        )
        move.action_post()
        return move.line_ids.filtered(
            lambda line: line.account_id.id == counterpart_account.id
        )

    def _reconcile_lines(self, lines, allow_partial=False):
        """Try to reconcile given lines

        :param list lines: list of dict of move lines, they must at least
                           contain values for : id, debit, credit, amount_residual and
                           amount_residual_currency
        :param boolean allow_partial: if True, partial reconciliation will be
                                      created, otherwise only Full
                                      reconciliation will be created
        :return: tuple of boolean values, first item is wether the items
                 have been reconciled or not,
                 the second is wether the reconciliation is full (True)
                 or partial (False)
        """
        self.ensure_one()
        ml_obj = self.env["account.move.line"]
        (
            below_writeoff,
            amount_writeoff,
            amount_writeoff_curr,
            same_curr,
        ) = self._below_writeoff_limit(lines, self.write_off)
        rec_date = self._get_rec_date(lines, self.date_base_on)
        line_rs = ml_obj.browse([line["id"] for line in lines]).with_context(
            date_p=rec_date, comment=_("Automatic Write Off")
        )
        if below_writeoff:
            balance = amount_writeoff_curr if same_curr else amount_writeoff
            if abs(balance) != 0.0:
                writeoff_line = self.create_write_off(
                    line_rs, amount_writeoff, amount_writeoff_curr, same_curr
                )
                line_rs |= writeoff_line
            line_rs.reconcile()
            return True, True
        elif allow_partial:
            line_rs.reconcile()
            return True, False
        return False, False
