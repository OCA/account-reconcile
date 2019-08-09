# Copyright 2017-2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import ast
import logging

from odoo import api, models
from odoo.addons.connector.queue.job import job
from odoo.addons.connector.session import ConnectorSession

_logger = logging.getLogger(__name__)


class AccountMassReconcile(models.Model):
    _inherit = 'account.mass.reconcile'

    @api.multi
    def run_reconcile(self):
        as_job = self.env['ir.config_parameter'].sudo().get_param(
            'account.mass.reconcile.as.job', default=False
        )
        try:
            as_job = ast.literal_eval(as_job) if as_job else False
        except ValueError:
            as_job = False

        for rec in self:
            if as_job:
                _super = super(
                    AccountMassReconcile,
                    rec.with_context(
                        mass_reconcile_as_job=True,
                        mass_reconcile_id=rec.id,
                    )
                )
            else:
                _super = super(AccountMassReconcile, rec)
            _super.run_reconcile()
        return True

    @api.multi
    def _run_reconcile_method(self, reconcile_method):
        _super = super(
            AccountMassReconcile,
            self.with_context(mass_reconcile_method_id=reconcile_method.id)
        )
        return _super._run_reconcile_method(reconcile_method)


def _rec_as_job(self, lines, allow_partial=False):
    mass_reconcile_id = self.env.context.get('mass_reconcile_id')
    method_id = self.env.context.get('mass_reconcile_method_id')
    assert mass_reconcile_id
    session = ConnectorSession.from_env(self.env)
    line_ids = [line['id'] for line in lines]
    _logger.debug("Delaying reconciliation of lines ids %s", line_ids)
    reconcile.delay(session, self._name, mass_reconcile_id,
                    method_id, line_ids, allow_partial=True,
                    priority=40)
    return True, False


class MassReconcileAdvancedRef(models.TransientModel):
    _inherit = 'mass.reconcile.advanced.ref'

    # TODO move method to a base class since it's the same for all classes?
    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        if self.env.context.get('mass_reconcile_as_job'):
            return _rec_as_job(self, lines, allow_partial=allow_partial)
        else:
            return super()._reconcile_lines(
                lines, allow_partial=allow_partial
            )


class MassReconcileAdvancedTransactionRef(models.TransientModel):
    _inherit = 'mass.reconcile.advanced.transaction_ref'

    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        if self.env.context.get('mass_reconcile_as_job'):
            return _rec_as_job(self, lines, allow_partial=allow_partial)
        else:
            return super()._reconcile_lines(
                lines, allow_partial=allow_partial
            )


class MassReconcileAdvancedTransRefvsRef(models.TransientModel):
    _inherit = 'mass.reconcile.advanced.transaction.ref.vs.ref'

    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        if self.env.context.get('mass_reconcile_as_job'):
            return _rec_as_job(self, lines, allow_partial=allow_partial)
        else:
            return super()._reconcile_lines(
                lines, allow_partial=allow_partial
            )


class MassReconcileReconcileRefDeepSearch(models.TransientModel):
    # account_mass_reconcile_ref_deep_search
    _inherit = 'mass.reconcile.advanced.ref.deep.search'

    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        if self.env.context.get('mass_reconcile_as_job'):
            return _rec_as_job(self, lines, allow_partial=allow_partial)
        else:
            return super()._reconcile_lines(
                lines, allow_partial=allow_partial
            )


@job(default_channel='root.mass_reconcile')
def reconcile(session, model_name, mass_reconcile_id, method_id,
              line_ids, allow_partial=True):
    """Reconcile a group of account move lines"""
    env = session.env
    fields = ['id', 'debit', 'credit', 'amount_residual', 'full_reconcile_id']
    lines = env['account.move.line'].browse(line_ids).exists()
    lines = lines.read(fields=fields)
    mass_model = env['account.mass.reconcile']
    mass_reconcile = mass_model.browse(mass_reconcile_id).exists()
    if not mass_reconcile:
        return 'mass reconcile %d no longer exists' % (mass_reconcile_id,)

    method = env['account.mass.reconcile.method'].browse(method_id).exists()
    if not method:
        return 'method %d no longer exists' % (method_id,)

    if any(line['full_reconcile_id'] for line in lines):
        return 'at least one of the lines is already reconciled'

    auto_rec = env[model_name].create(
        mass_reconcile._prepare_run_transient(method)
    )
    reconciled, full = auto_rec._reconcile_lines(
        lines, allow_partial=allow_partial
    )
    if reconciled:
        word = 'fully' if full else 'partially'
    else:
        word = 'not'
    return 'lines %s %s reconciled' % (line_ids, word)
