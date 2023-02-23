# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MassReconcileHistory(models.Model):
    """Store an history of the runs per profile

    Each history stores the list of reconciliations done
    """

    _name = "mass.reconcile.history"
    _description = "Store an history of the runs per profile"
    _rec_name = "mass_reconcile_id"
    _order = "date DESC"

    @api.depends("reconcile_ids")
    def _compute_reconcile_line_ids(self):
        for rec in self:
            rec.reconcile_line_ids = rec.mapped("reconcile_ids.reconciled_line_ids").ids

    mass_reconcile_id = fields.Many2one(
        "account.mass.reconcile", string="Reconcile Profile", readonly=True
    )
    date = fields.Datetime(string="Run date", readonly=True, required=True)
    reconcile_ids = fields.Many2many(
        comodel_name="account.full.reconcile",
        relation="account_full_reconcile_history_rel",
        string="Full Reconciliations",
        readonly=True,
    )
    reconcile_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="account_move_line_history_rel",
        string="Reconciled Items",
        compute="_compute_reconcile_line_ids",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        store=True,
        readonly=True,
        related="mass_reconcile_id.company_id",
    )

    def _open_move_lines(self):
        """For an history record, open the view of move line with
        the reconciled move lines

        :param history_id: id of the history
        :return: action to open the move lines
        """
        move_line_ids = self.mapped("reconcile_ids.reconciled_line_ids").ids
        name = _("Reconciliations")
        return {
            "name": name,
            "view_mode": "tree,form",
            "view_id": False,
            "res_model": "account.move.line",
            "type": "ir.actions.act_window",
            "context": {"nodestroy": True},
            "target": "current",
            "domain": [("id", "in", move_line_ids)],
        }

    def open_reconcile(self):
        """For an history record, open the view of move line
        with the reconciled move lines

        :param history_ids: id of the record as int or long
                            Accept a list with 1 id too to be
                            used from the client.
        """
        self.ensure_one()
        return self._open_move_lines()
