# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
import logging

from odoo import models, api, fields, _
from odoo.exceptions import Warning as UserError
from odoo import sql_db

_logger = logging.getLogger(__name__)


class MassReconcileOptions(models.AbstractModel):
    """Options of a reconciliation profile

    Columns shared by the configuration of methods
    and by the reconciliation wizards.
    This allows decoupling of the methods and the
    wizards and allows to launch the wizards alone
    """
    _name = 'mass.reconcile.options'
    _description = 'Options of a reconciliation profile'

    @api.model
    def _get_rec_base_date(self):
        return [
            ('newest', 'Most recent move line'),
            ('actual', 'Today'),
        ]

    write_off = fields.Float(
        'Write off allowed',
        default=0.,
    )
    account_lost_id = fields.Many2one(
        'account.account',
        string="Account Lost",
    )
    account_profit_id = fields.Many2one(
        'account.account',
        string="Account Profit",
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
    )
    date_base_on = fields.Selection(
        '_get_rec_base_date',
        required=True,
        string='Date of reconciliation',
        default='newest',
    )
    _filter = fields.Char(
        string='Filter', oldname='filter',
    )
    income_exchange_account_id = fields.Many2one(
        'account.account',
        string='Gain Exchange Rate Account',
    )
    expense_exchange_account_id = fields.Many2one(
        'account.account',
        string='Loss Exchange Rate Account',
    )


class AccountMassReconcileMethod(models.Model):
    _name = 'account.mass.reconcile.method'
    _description = 'reconcile method for account_mass_reconcile'
    _inherit = 'mass.reconcile.options'
    _order = 'sequence'

    @staticmethod
    def _get_reconcilation_methods():
        return [
            ('mass.reconcile.simple.name', 'Simple. Amount and Name'),
            ('mass.reconcile.simple.partner', 'Simple. Amount and Partner'),
            ('mass.reconcile.simple.reference',
             'Simple. Amount and Reference'),
            ('mass.reconcile.advanced.ref',
             'Advanced. Partner and Ref.'),
        ]

    def _selection_name(self):
        return self._get_reconcilation_methods()

    name = fields.Selection(
        '_selection_name',
        string='Type',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=1,
        required=True,
        help="The sequence field is used to order the reconcile method",
    )
    task_id = fields.Many2one(
        'account.mass.reconcile',
        string='Task',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related="task_id.company_id",
        store=True,
        readonly=True,
    )


class AccountMassReconcile(models.Model):
    _name = 'account.mass.reconcile'
    _inherit = ['mail.thread']
    _description = 'account mass reconcile'

    @api.multi
    @api.depends('account', 'history_ids')
    def _get_total_unrec(self):
        obj_move_line = self.env['account.move.line']
        for rec in self:
            rec.unreconciled_count = obj_move_line.search_count(
                [('account_id', '=', rec.account.id),
                 ('reconciled', '=', False)])

    @api.multi
    @api.depends('history_ids')
    def _last_history(self):
        # do a search() for retrieving the latest history line,
        # as a read() will badly split the list of ids with 'date desc'
        # and return the wrong result.
        history_obj = self.env['mass.reconcile.history']
        for rec in self:
            last_history_rs = history_obj.search(
                [('mass_reconcile_id', '=', rec.id)],
                limit=1, order='date desc'
                )
            rec.last_history = last_history_rs or False

    name = fields.Char(
        string='Name',
        required=True,
    )
    account = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
    )
    reconcile_method = fields.One2many(
        'account.mass.reconcile.method',
        'task_id',
        string='Method',
    )
    unreconciled_count = fields.Integer(
        string='Unreconciled Items',
        compute='_get_total_unrec',
    )
    history_ids = fields.One2many(
        'mass.reconcile.history',
        'mass_reconcile_id',
        string='History',
        readonly=True,
    )
    last_history = fields.Many2one(
        'mass.reconcile.history',
        string='Last history', readonly=True,
        compute='_last_history',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )

    @staticmethod
    def _prepare_run_transient(rec_method):
        return {'account_id': rec_method.task_id.account.id,
                'write_off': rec_method.write_off,
                'account_lost_id': (rec_method.account_lost_id.id),
                'account_profit_id': (rec_method.account_profit_id.id),
                'income_exchange_account_id':
                (rec_method.income_exchange_account_id.id),
                'expense_exchange_account_id':
                (rec_method.income_exchange_account_id.id),
                'journal_id': (rec_method.journal_id.id),
                'date_base_on': rec_method.date_base_on,
                '_filter': rec_method._filter}

    @api.multi
    def run_reconcile(self):
        def find_reconcile_ids(fieldname, move_line_ids):
            if not move_line_ids:
                return []
            sql = ("SELECT DISTINCT " + fieldname +
                   " FROM account_move_line "
                   " WHERE id in %s "
                   " AND " + fieldname + " IS NOT NULL")
            self.env.cr.execute(sql, (tuple(move_line_ids),))
            res = self.env.cr.fetchall()
            return [row[0] for row in res]

        # we use a new cursor to be able to commit the reconciliation
        # often. We have to create it here and not later to avoid problems
        # where the new cursor sees the lines as reconciles but the old one
        # does not.

        for rec in self:
            ctx = self.env.context.copy()
            ctx['commit_every'] = (
                rec.account.company_id.reconciliation_commit_every
            )
            if ctx['commit_every']:
                new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            else:
                new_cr = self.env.cr

            try:
                all_ml_rec_ids = []

                for method in rec.reconcile_method:
                    rec_model = self.env[method.name]
                    auto_rec_id = rec_model.create(
                        self._prepare_run_transient(method)
                        )

                    ml_rec_ids = auto_rec_id.automatic_reconcile()

                    all_ml_rec_ids += ml_rec_ids

                reconcile_ids = find_reconcile_ids(
                    'full_reconcile_id',
                    all_ml_rec_ids
                )
                self.env['mass.reconcile.history'].create(
                    {
                        'mass_reconcile_id': rec.id,
                        'date': fields.Datetime.now(),
                        'reconcile_ids': [
                            (4, rid) for rid in reconcile_ids
                            ],
                    })
            except Exception as e:
                # In case of error, we log it in the mail thread, log the
                # stack trace and create an empty history line; otherwise,
                # the cron will just loop on this reconcile task.
                _logger.exception(
                    "The reconcile task %s had an exception: %s",
                    rec.name, str(e)
                )
                message = _("There was an error during reconciliation : %s") \
                    % str(e)
                rec.message_post(body=message)
                self.env['mass.reconcile.history'].create(
                    {
                        'mass_reconcile_id': rec.id,
                        'date': fields.Datetime.now(),
                        'reconcile_ids': [],
                    }
                )
            finally:
                if ctx['commit_every']:
                    new_cr.commit()
                    new_cr.close()

        return True

    def _no_history(self):
        """ Raise an `orm.except_orm` error, supposed to
        be called when there is no history on the reconciliation
        task.
        """
        raise UserError(
            _('There is no history of reconciled '
              'items on the task: %s.') % self.name
        )

    @staticmethod
    def _open_move_line_list(move_line_ids, name):
        return {
            'name': name,
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': [('id', 'in', move_line_ids)],
        }

    @api.multi
    def open_unreconcile(self):
        """ Open the view of move line with the unreconciled move lines"""
        self.ensure_one()
        obj_move_line = self.env['account.move.line']
        lines = obj_move_line.search(
            [('account_id', '=', self.account.id),
             ('reconciled', '=', False)])
        name = _('Unreconciled items')
        return self._open_move_line_list(lines.ids or [], name)

    def last_history_reconcile(self):
        """ Get the last history record for this reconciliation profile
        and return the action which opens move lines reconciled
        """
        if not self.last_history:
            self._no_history()
        return self.last_history.open_reconcile()

    @api.model
    def run_scheduler(self, run_all=None):
        """ Launch the reconcile with the oldest run
        This function is mostly here to be used with cron task

        :param run_all: if set it will ingore lookup and launch
                    all reconciliation
        :returns: True in case of success or raises an exception

        """
        def _get_date(reconcile):
            if reconcile.last_history.date:
                return fields.Datetime.to_datetime(reconcile.last_history.date)
            else:
                return datetime.min

        reconciles = self.search([])
        assert reconciles.ids, "No mass reconcile available"
        if run_all:
            reconciles.run_reconcile()
            return True
        reconciles.sorted(key=_get_date)
        older = reconciles[0]
        older.run_reconcile()
        return True
