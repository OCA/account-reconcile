# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class AccountMoveLineReconcileManual(models.TransientModel):
    _name = "account.move.line.reconcile.manual"
    _description = "Manual Reconciliation Wizard"
    _check_company_auto = True

    account_id = fields.Many2one(
        "account.account", required=True, readonly=True, check_company=True
    )
    company_id = fields.Many2one("res.company", required=True, readonly=True)
    currency_id = fields.Many2one("res.currency")
    company_currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id"
    )
    count = fields.Integer(string="# of Journal Items", readonly=True)
    total_debit = fields.Monetary(currency_field="currency_id", readonly=True)
    total_credit = fields.Monetary(currency_field="currency_id", readonly=True)
    move_line_ids = fields.Many2many(
        "account.move.line", readonly=True, check_company=True
    )
    partner_count = fields.Integer(readonly=True)
    partner_id = fields.Many2one("res.partner", readonly=True)
    state = fields.Selection(
        [
            ("start", "Start"),
            ("writeoff", "Write-off"),
        ],
        readonly=True,
        default="start",
    )
    # START WRITE-OFF FIELDS
    writeoff_currency_id = fields.Many2one("res.currency")
    writeoff_model_id = fields.Many2one(
        "account.reconcile.manual.model",
        string="Model",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    writeoff_journal_id = fields.Many2one(
        "account.journal",
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Journal",
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        check_company=True,
    )
    writeoff_date = fields.Date(string="Date", default=fields.Date.context_today)
    writeoff_ref = fields.Char(
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Reference",
        default=lambda self: _("Write-off"),
    )
    writeoff_type = fields.Selection(
        [
            ("income", "Income"),
            ("expense", "Expense"),
            ("none", "None"),
        ],
        readonly=True,
        string="Type",
    )
    writeoff_amount = fields.Monetary(
        currency_field="company_currency_id", readonly=True, string="Amount"
    )
    writeoff_amount_currency = fields.Monetary(
        currency_field="writeoff_currency_id", readonly=True, string="Amount Currency"
    )
    writeoff_account_id = fields.Many2one(
        "account.account",
        compute="_compute_writeoff",
        readonly=False,
        store=True,
        precompute=True,
        string="Write-off Account",
        domain="[('company_ids', '=', company_id), ('deprecated', '=', False)]",
        check_company=True,
    )
    writeoff_analytic_distribution = fields.Json(
        string="Analytic",
        compute="_compute_writeoff_analytic_distribution",
        readonly=False,
        store=True,
        precompute=True,
    )
    analytic_precision = fields.Integer(
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )
    is_multi_currency = fields.Boolean()

    @api.depends("writeoff_model_id")
    def _compute_writeoff(self):
        for wiz in self:
            if wiz.writeoff_model_id:
                model = wiz.writeoff_model_id
                wiz.writeoff_journal_id = model.journal_id
                wiz.writeoff_ref = model.ref
                if wiz.writeoff_type == "expense":
                    wiz.writeoff_account_id = model.expense_account_id.id
                    if model.expense_analytic_distribution:
                        wiz.writeoff_analytic_distribution = (
                            model.expense_analytic_distribution
                        )
                elif wiz.writeoff_type == "income":
                    wiz.writeoff_account_id = model.income_account_id.id
                    if model.income_analytic_distribution:
                        wiz.writeoff_analytic_distribution = (
                            model.income_analytic_distribution
                        )
            else:
                journals = self.env["account.journal"].search(
                    [("type", "=", "general"), ("company_id", "=", wiz.company_id.id)]
                )
                if len(journals) == 1:
                    wiz.writeoff_journal_id = journals.id

    @api.depends("writeoff_account_id")
    def _compute_writeoff_analytic_distribution(self):
        aadmo = self.env["account.analytic.distribution.model"]
        for wiz in self:
            if wiz.writeoff_account_id and not wiz.writeoff_analytic_distribution:
                wiz.writeoff_analytic_distribution = aadmo._get_distribution(
                    {
                        "account_prefix": wiz.writeoff_account_id.code,
                        "company_id": wiz.company_id.id,
                    }
                )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get("active_model") == self._name:  # write-off step
            return res
        assert self._context.get("active_model") == "account.move.line"
        move_lines = self.env["account.move.line"].browse(
            self._context.get("active_ids")
        )
        company = move_lines.company_id
        if len(company) > 1:
            raise UserError(self.env._("All lines must belong to the same company"))
        ccur = company.currency_id
        count = 0
        account = False
        total_debit = total_credit = 0.0
        partner_set = set()
        currencies = move_lines.currency_id
        currency = len(currencies) == 1 and currencies or ccur
        is_foreign_currency = currency != ccur
        for line in move_lines:
            count += 1
            if is_foreign_currency:
                debit = (
                    line.amount_residual_currency > 0.0
                    and line.amount_residual_currency
                    or 0.0
                )
                credit = (
                    line.amount_residual_currency < 0.0
                    and abs(line.amount_residual_currency)
                    or 0.0
                )
            else:
                debit = line.amount_residual > 0.0 and line.amount_residual or 0.0
                credit = line.amount_residual < 0.0 and abs(line.amount_residual) or 0.0
            total_debit += debit
            total_credit += credit
            if line.reconciled:
                raise UserError(
                    _("Line '%s' is already fully reconciled.") % line.display_name
                )
            if account:
                if account != line.account_id:
                    raise UserError(
                        _(
                            "The Journal Items selected have different accounts: "
                            "%(account1)s and %(account2)s.",
                            account1=account.code,
                            account2=line.account_id.code,
                        )
                    )
            else:
                account = line.account_id
            if line.partner_id:
                partner_set.add(line.partner_id.id)
        if not account.reconcile:
            raise UserError(
                _("Account '%s' is not reconciliable.") % account.display_name
            )
        if count <= 1:
            raise UserError(_("You must select at least 2 journal items!"))
        if currency.is_zero(total_debit):
            raise UserError(_("You selected only credit journal items."))
        if currency.is_zero(total_credit):
            raise UserError(_("You selected only debit journal items."))
        total_debit = currency.round(total_debit)
        total_credit = currency.round(total_credit)
        compare_res = currency.compare_amounts(total_debit, total_credit)
        if compare_res > 0:
            writeoff_type = "expense"
        elif compare_res < 0:
            writeoff_type = "income"
        else:
            writeoff_type = "none"
        res.update(
            {
                "count": count,
                "account_id": account.id,
                "company_id": company.id,
                "currency_id": currency.id,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "partner_count": len(partner_set),
                "partner_id": len(partner_set) == 1 and partner_set.pop() or False,
                "move_line_ids": move_lines.ids,
                "is_multi_currency": len(currencies) > 1,
                "writeoff_type": writeoff_type,
            }
        )
        return res

    def full_reconcile(self):
        self.ensure_one()
        no_exchange_difference = len(self.move_line_ids.currency_id) > 1 or False
        self.move_line_ids.with_context(
            no_exchange_difference=no_exchange_difference
        ).reconcile()
        for move_line in self.move_line_ids:
            if not move_line.reconciled:
                raise UserError(
                    _("Full reconciliation failed. It should never happen!")
                )
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Successful reconciliation"),
                "message": _("Reconcile mark: %s")
                % self.move_line_ids.full_reconcile_id.display_name,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return action

    def partial_reconcile(self):
        self.ensure_one()
        self.move_line_ids.reconcile()
        return

    def _get_writeoff_vals_by_simulation(self):
        """
        In some multi-currency reconciliation cases, it is too complicated to 'guess'
        the required write-off amounts. For these cases, we simulate the reconciliation
        to obtain the actual write-off amounts.
        """
        amls = self.move_line_ids
        # From _reconcile_plan_with_sync
        plan_list, all_amls = self.env[
            "account.move.line"
        ]._optimize_reconciliation_plan([amls])
        aml_values_map = {
            aml: {
                "aml": aml,
                "amount_residual": aml.amount_residual,
                "amount_residual_currency": aml.amount_residual_currency,
            }
            for aml in all_amls
        }
        plan = plan_list[0]
        # Simulate the reconciliation
        # disable exchange difference because the writeoff will take care of it
        # anyway.
        self.env["account.move.line"].with_context(
            no_exchange_difference=True
        )._prepare_reconciliation_plan(plan, aml_values_map)

        # aml_values_map is updated by the simulation, check residuals in order to
        # compute the writeoff amounts we need to complete the reconciliation

        residual_lines = self.env["account.move.line"]
        residual = residual_currency = 0.0
        currency = False
        writeoff = True
        for aml, vals in aml_values_map.items():
            if vals["amount_residual"] or vals["amount_residual_currency"]:
                residual_lines |= aml
                residual += vals["amount_residual"]
                residual_currency += vals["amount_residual_currency"]
                if not currency:
                    currency = aml.currency_id
                if currency != aml.currency_id:
                    writeoff = False
                    break
        if not writeoff:
            return False
        return {
            "writeoff_amount": -residual,
            "writeoff_amount_currency": -residual_currency,
            "writeoff_currency_id": currency.id,
        }

    def _compute_writeoff_amounts(self):
        # avoid redoing simulation if we do have the amounts already
        if self.writeoff_amount or self.writeoff_amount_currency:
            return
        if self.is_multi_currency:
            vals = self._get_writeoff_vals_by_simulation()
            if vals:
                self.write(vals)
            else:
                raise UserError(
                    self.env._(
                        "Can't compute the writeoff amount, it may be caused by too "
                        "much currencies to be reconciled together. Yoy should probably"
                        " do a partial reconciliation and create the required write-off"
                        " entries manually to fully reconcile the remaining "
                        "unreconciled entries."
                    )
                )

        else:
            writeoff_amount = self.currency_id.round(
                -(self.total_debit - self.total_credit)
            )
            if self.currency_id != self.company_currency_id:
                self.write(
                    {
                        "writeoff_amount_currency": writeoff_amount,
                        "writeoff_currency_id": self.currency_id.id,
                    }
                )
            else:
                self.write(
                    {
                        "writeoff_amount": writeoff_amount,
                        "writeoff_currency_id": self.currency_id.id,
                    }
                )

    def go_to_writeoff(self):
        self.ensure_one()
        self._compute_writeoff_amounts()
        self.write({"state": "writeoff"})
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_move_line_reconcile_manual.account_move_line_reconcile_manual_action"
        )
        action["res_id"] = self.id
        return action

    def _prepare_writeoff_move(self):
        # TODO manage case with not computed ccur amount
        # Manage case of + currency and - euro ?
        # could strategy be : partial reconcile
        # reconcile resildual with write off by currency ?
        cur = self.writeoff_currency_id
        is_foreign_currency = self.company_currency_id != self.writeoff_currency_id

        bal_cur = cur.round(self.writeoff_amount_currency)
        bal = self.company_id.currency_id.round(self.writeoff_amount)
        compare_res = cur.compare_amounts(bal, 0)
        debit = credit = 0.0
        if compare_res > 0:
            debit = bal
        else:
            credit = bal * -1
        payment_term_line_vals = {
            "display_type": "payment_term",
            "account_id": self.account_id.id,
            "partner_id": self.partner_id and self.partner_id.id or False,
        }

        product_line_vals = {
            "display_type": "product",
            "account_id": self.writeoff_account_id.id,
            "partner_id": self.partner_id and self.partner_id.id or False,
            "analytic_distribution": self.writeoff_analytic_distribution,
        }
        if is_foreign_currency:
            payment_term_line_vals.update(
                {
                    "currency_id": cur.id,
                    "amount_currency": bal_cur,
                }
            )
            product_line_vals.update(
                {
                    "currency_id": cur.id,
                    "amount_currency": -bal_cur,
                }
            )
            # in multi currency mode, we simulate the reconciliation and we know
            # both currency and company currency amounts while in normal case (mono
            # currency reconciliation) we leave Odoo generates the exchange rate entries
            if self.is_multi_currency:
                payment_term_line_vals.update(
                    {
                        "debit": debit,
                        "credit": credit,
                    }
                )
                product_line_vals.update(
                    {
                        "debit": credit,
                        "credit": debit,
                    }
                )
        else:
            payment_term_line_vals.update({"debit": debit, "credit": credit})
            product_line_vals.update(
                {
                    "debit": credit,
                    "credit": debit,
                }
            )

        vals = {
            "company_id": self.company_id.id,
            "journal_id": self.writeoff_journal_id.id,
            "ref": self.writeoff_ref,
            "date": self.writeoff_date,
            "line_ids": [
                (
                    0,
                    0,
                    payment_term_line_vals,
                ),
                (
                    0,
                    0,
                    product_line_vals,
                ),
            ],
        }
        if is_foreign_currency:
            vals["currency_id"] = cur.id
        return vals

    def reconcile_with_writeoff(self):
        self.ensure_one()
        assert self.writeoff_journal_id
        assert self.writeoff_date
        assert self.writeoff_account_id
        assert self.state == "writeoff"
        vals = self._prepare_writeoff_move()
        woff_move = self.env["account.move"].create(vals)
        woff_move.with_context(validate_analytic=True)._post(soft=False)
        to_rec_woff_line = woff_move.line_ids.filtered(
            lambda x: x.account_id.id == self.account_id.id
        )
        assert len(to_rec_woff_line) == 1
        no_exchange_difference = len(self.move_line_ids.currency_id) > 1 or False
        self.env["account.move.line"].with_context(
            no_exchange_difference=no_exchange_difference
        )._reconcile_plan([[self.move_line_ids, to_rec_woff_line]])
        for move_line in self.move_line_ids:
            if not move_line.reconciled:
                raise UserError(
                    _("Full reconciliation failed. It should never happen!")
                )
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Successful reconciliation"),
                "message": _(
                    "Write-off journal entry: %(writeoff_move)s\n\
                    Reconcile mark: %(full_rec)s",
                    full_rec=self.move_line_ids[0].full_reconcile_id.display_name,
                    writeoff_move=woff_move.name,
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return action

    @api.onchange("writeoff_account_id")
    def writeoff_account_id_change(self):
        account = self.writeoff_account_id
        if (
            self.writeoff_type in ("income", "expense")
            and account
            and self.writeoff_type not in account.account_type
        ):
            message = _(
                "This is a/an '%(writeoff_type)s' write-off, "
                "but you selected account %(account_code)s "
                "which is a/an '%(account_type)s' account.",
                writeoff_type=self._fields["writeoff_type"].convert_to_export(
                    self.writeoff_type, self
                ),
                account_code=account.code,
                account_type=account._fields["account_type"].convert_to_export(
                    account.account_type, account
                ),
            )
            res = {
                "warning": {
                    "title": _("Bad write-off account type"),
                    "message": message,
                }
            }
            return res
