# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, tools


class AccountReconcilePartnerMismatchReport(models.Model):
    _name = "account.reconcile.partner.mismatch.report"
    _description = "Account Reconcile Partner Mismatch Report"
    _auto = False

    partial_reconcile_id = fields.Many2one(
        "account.partial.reconcile", string="Partial Reconcile"
    )
    full_reconcile_id = fields.Many2one("account.full.reconcile")
    account_id = fields.Many2one("account.account", string="Account")
    account_type_id = fields.Many2one("account.account.type", string="Account type")
    debit_move_id = fields.Many2one("account.move.line", string="Debit move")
    debit_amount = fields.Float("Debit amount")
    debit_partner_id = fields.Many2one("res.partner", string="Debit partner")
    credit_move_id = fields.Many2one("account.move.line", string="Credit move")
    credit_amount = fields.Float("Credit amount")
    credit_partner_id = fields.Many2one("res.partner", string="Credit partner")

    def init(self):
        """Select lines which violate defined rules"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
                    SELECT pr.id id
                    , pr.id partial_reconcile_id
                    , pr.full_reconcile_id
                    , pr.debit_move_id
                    , daml.debit debit_amount
                    , aat.id account_type_id
                    , daml.partner_id debit_partner_id
                    , daml.account_id account_id
                    , pr.credit_move_id
                    , caml.credit credit_amount
                    , caml.partner_id credit_partner_id
                    FROM account_partial_reconcile  pr
                    LEFT JOIN account_move_line daml
                        ON daml.id = pr.debit_move_id
                    LEFT JOIN account_move_line caml
                        ON caml.id = pr.credit_move_id
                    LEFT JOIN account_account aa
                        ON daml.account_id = aa.id
                    LEFT JOIN account_account_type aat
                        ON aa.user_type_id = aat.id
                    WHERE aat.type in ('receivable', 'payable')
                    AND (daml.partner_id <> caml.partner_id
                    OR (daml.partner_id IS NULL
                        AND caml.partner_id IS NOT NULL)
                    OR (caml.partner_id IS NULL
                        AND daml.partner_id IS NOT NULL))
                )
        """
            % self._table
        )
