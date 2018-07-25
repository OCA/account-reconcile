# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import reduce
from operator import itemgetter

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class MassReconcileBase(models.AbstractModel):
    """Abstract Model for reconciliation methods"""
    _name = 'mass.reconcile.base'
    _inherit = 'mass.reconcile.options'

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Restrict on partners',
    )
    # other fields are inherited from mass.reconcile.options

    @api.multi
    def automatic_reconcile(self):
        """ Reconciliation method called from the view.

        :return: list of reconciled ids
        """
        self.ensure_one()
        return self._action_rec()

    def _action_rec(self):
        """ Must be inherited to implement the reconciliation

        :return: list of reconciled ids
        """
        raise NotImplementedError

    @staticmethod
    def _base_columns():
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = (
            'id',
            'debit',
            'credit',
            'date',
            'ref',
            'name',
            'partner_id',
            'account_id',
            'reconciled',
            'move_id',
        )
        return ["account_move_line.{}".format(col) for col in aml_cols]

    def _selection_columns(self):
        return self._base_columns()

    def _select_query(self, *args, **kwargs):
        return "SELECT %s" % ', '.join(self._selection_columns())

    def _from_query(self, *args, **kwargs):
        return ("FROM account_move_line ")

    @api.multi
    def _where_query(self, *args, **kwargs):
        self.ensure_one()
        where = ("WHERE account_move_line.account_id = %s "
                 "AND NOT account_move_line.reconciled")
        # it would be great to use dict for params
        # but as we use _where_calc in _get_filter
        # which returns a list, we have to
        # accomodate with that
        params = [self.account_id.id]
        if self.partner_ids:
            where += " AND account_move_line.partner_id IN %s"
            params.append(tuple([l.id for l in self.partner_ids]))
        return where, params

    @api.multi
    def _get_filter(self):
        self.ensure_one()
        ml_obj = self.env['account.move.line']
        where = ''
        params = []
        if self._filter:
            dummy, where, params = ml_obj._where_calc(
                safe_eval(self._filter)).get_sql()
            if where:
                where = " AND %s" % where
        return where, params

    @api.multi
    def _below_writeoff_limit(self, lines, writeoff_limit):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Account')
        keys = ('debit', 'credit')
        sums = reduce(
            lambda line, memo:
            dict((key, value + memo[key])
                 for key, value
                 in line.items()
                 if key in keys), lines)
        debit, credit = sums['debit'], sums['credit']
        writeoff_amount = round(debit - credit, precision)
        return bool(writeoff_limit >= abs(writeoff_amount)), debit, credit

    @api.multi
    def _get_rec_date(self, lines, based_on='end_period_last_credit'):
        self.ensure_one()

        def last_date(mlines):
            return max(mlines, key=itemgetter('date'))

        def credit(mlines):
            return [l for l in mlines if l['credit'] > 0]

        def debit(mlines):
            return [l for l in mlines if l['debit'] > 0]

        if based_on == 'newest':
            return last_date(lines)['date']
        elif based_on == 'newest_credit':
            return last_date(credit(lines))['date']
        elif based_on == 'newest_debit':
            return last_date(debit(lines))['date']
        # reconcilation date will be today
        # when date is None
        return None

    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        """ Try to reconcile given lines

        :param list lines: list of dict of move lines, they must at least
                           contain values for : id, debit, credit
        :param boolean allow_partial: if True, partial reconciliation will be
                                      created, otherwise only Full
                                      reconciliation will be created
        :return: tuple of boolean values, first item is wether the items
                 have been reconciled or not,
                 the second is wether the reconciliation is full (True)
                 or partial (False)
        """
        self.ensure_one()
        ml_obj = self.env['account.move.line']
        below_writeoff, sum_debit, sum_credit = self._below_writeoff_limit(
            lines, self.write_off
        )
        rec_date = self._get_rec_date(lines, self.date_base_on)
        line_rs = ml_obj.browse([l['id'] for l in lines]).with_context(
            date_p=rec_date,
            comment=_('Automatic Write Off'))
        if below_writeoff:
            if sum_credit > sum_debit:
                writeoff_account = self.account_profit_id
            else:
                writeoff_account = self.account_lost_id
            line_rs.reconcile(
                writeoff_acc_id=writeoff_account,
                writeoff_journal_id=self.journal_id
            )
            return True, True
        elif allow_partial:
            # We need to give a writeoff_acc_id
            # in case we have a multi currency lines
            # to reconcile.
            # If amount in currency is equal between
            # lines to reconcile
            # it will do a full reconcile instead of a partial reconcile
            # and make a write-off for exchange
            if sum_credit > sum_debit:
                writeoff_account = self.income_exchange_account_id
            else:
                writeoff_account = self.expense_exchange_account_id
            line_rs.reconcile(
                writeoff_acc_id=writeoff_account,
                writeoff_journal_id=self.journal_id
            )
            return True, False
        return False, False
