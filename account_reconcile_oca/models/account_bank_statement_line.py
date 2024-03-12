# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = ["account.bank.statement.line", "account.reconcile.abstract"]

    reconcile_data_info = fields.Serialized(inverse="_inverse_reconcile_data_info")
    reconcile_mode = fields.Selection(
        selection=lambda self: self.env["account.journal"]
        ._fields["reconcile_mode"]
        .selection
    )
    company_id = fields.Many2one(related="journal_id.company_id")
    reconcile_data = fields.Serialized()
    manual_line_id = fields.Many2one(
        "account.move.line",
        store=False,
        default=False,
        prefetch=False,
    )
    manual_kind = fields.Char(
        store=False,
        default=False,
        prefetch=False,
    )
    manual_account_id = fields.Many2one(
        "account.account",
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
    )
    manual_partner_id = fields.Many2one(
        "res.partner",
        domain=[("parent_id", "=", False)],
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
    )
    analytic_distribution = fields.Json(
        store=False,
        default=False,
        prefetch=False,
    )
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )
    manual_model_id = fields.Many2one(
        "account.reconcile.model",
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
        domain=[("rule_type", "=", "writeoff_button")],
    )
    manual_name = fields.Char(store=False, default=False, prefetch=False)
    manual_amount = fields.Monetary(
        store=False, default=False, prefetch=False, currency_field="manual_currency_id"
    )
    manual_currency_id = fields.Many2one(
        "res.currency", readonly=True, store=False, prefetch=False
    )
    manual_original_amount = fields.Monetary(
        default=False, store=False, prefetch=False, readonly=True
    )
    manual_move_type = fields.Selection(
        lambda r: r.env["account.move"]._fields["move_type"].selection,
        default=False,
        store=False,
        prefetch=False,
        readonly=True,
    )
    manual_move_id = fields.Many2one(
        "account.move", default=False, store=False, prefetch=False, readonly=True
    )
    can_reconcile = fields.Boolean(sparse="reconcile_data_info")

    def save(self):
        return {"type": "ir.actions.act_window_close"}

    @api.model
    def action_new_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.action_bank_statement_line_create"
        )
        action["context"] = self.env.context
        return action

    @api.onchange("manual_model_id")
    def _onchange_manual_model_id(self):
        if self.manual_model_id:
            data = []
            for line in self.reconcile_data_info.get("data", []):
                if line.get("kind") != "suspense":
                    data.append(line)
            self.reconcile_data_info = self._recompute_suspense_line(
                *self._reconcile_data_by_model(
                    data,
                    self.manual_model_id,
                    self.reconcile_data_info["reconcile_auxiliary_id"],
                ),
                self.manual_reference
            )
        else:
            # Refreshing data
            self.reconcile_data_info = self.browse(
                self.id.origin
            )._default_reconcile_data()
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    @api.onchange("add_account_move_line_id")
    def _onchange_add_account_move_line_id(self):
        if self.add_account_move_line_id:
            data = self.reconcile_data_info["data"]
            new_data = []
            is_new_line = True
            pending_amount = 0.0
            for line in data:
                if line["kind"] != "suspense":
                    pending_amount += line["amount"]
                if line.get("counterpart_line_id") == self.add_account_move_line_id.id:
                    is_new_line = False
                else:
                    new_data.append(line)
            if is_new_line:
                new_data.append(
                    self._get_reconcile_line(
                        self.add_account_move_line_id, "other", True, pending_amount
                    )
                )
            self.reconcile_data_info = self._recompute_suspense_line(
                new_data,
                self.reconcile_data_info["reconcile_auxiliary_id"],
                self.manual_reference,
                exchange_recompute=True,
            )
            self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)
            self.add_account_move_line_id = False

    def _recompute_suspense_line(
        self, data, reconcile_auxiliary_id, manual_reference, exchange_recompute=False
    ):
        reconcile_auxiliary_id = self._compute_exchange_rate(
            data, reconcile_auxiliary_id, exchange_recompute=exchange_recompute
        )
        can_reconcile = True
        total_amount = 0
        new_data = []
        suspense_line = False
        counterparts = []
        for line in data:
            if line.get("counterpart_line_id"):
                counterparts.append(line["counterpart_line_id"])
            if (
                line["account_id"][0] == self.journal_id.suspense_account_id.id
                or not line["account_id"][0]
            ) and line["kind"] != "suspense":
                can_reconcile = False
            if line["kind"] != "suspense":
                new_data.append(line)
                total_amount += line["amount"]
            else:
                suspense_line = line
        if not float_is_zero(
            total_amount, precision_digits=self.currency_id.decimal_places
        ):
            can_reconcile = False
            if suspense_line:
                suspense_line.update(
                    {
                        "amount": -total_amount,
                        "credit": total_amount if total_amount > 0 else 0.0,
                        "debit": -total_amount if total_amount < 0 else 0.0,
                    }
                )
            else:
                suspense_line = {
                    "reference": "reconcile_auxiliary;%s" % reconcile_auxiliary_id,
                    "id": False,
                    "account_id": self.journal_id.suspense_account_id.name_get()[0],
                    "partner_id": self.partner_id
                    and self.partner_id.name_get()[0]
                    or (False, self.partner_name),
                    "date": fields.Date.to_string(self.date),
                    "name": self.payment_ref or self.name,
                    "amount": -total_amount,
                    "credit": total_amount if total_amount > 0 else 0.0,
                    "debit": -total_amount if total_amount < 0 else 0.0,
                    "kind": "suspense",
                    "currency_id": self.company_id.currency_id.id,
                    "line_currency_id": self.company_id.currency_id.id,
                    "currency_amount": -total_amount,
                }
                reconcile_auxiliary_id += 1
            new_data.append(suspense_line)
        return {
            "data": new_data,
            "counterparts": counterparts,
            "reconcile_auxiliary_id": reconcile_auxiliary_id,
            "can_reconcile": can_reconcile,
            "manual_reference": manual_reference,
        }

    def _check_line_changed(self, line):
        return (
            not float_is_zero(
                self.manual_amount - line["amount"],
                precision_digits=self.company_id.currency_id.decimal_places,
            )
            or self.manual_account_id.id != line["account_id"][0]
            or self.manual_name != line["name"]
            or (
                self.manual_partner_id and self.manual_partner_id.name_get()[0] or False
            )
            != line.get("partner_id")
        )

    @api.onchange("manual_reference", "manual_delete")
    def _onchange_manual_reconcile_reference(self):
        self.ensure_one()
        data = self.reconcile_data_info.get("data", [])
        new_data = []
        for line in data:
            if line["reference"] == self.manual_reference:
                if self.manual_delete:
                    self.update(
                        {
                            "manual_delete": False,
                            "manual_reference": False,
                            "manual_account_id": False,
                            "manual_amount": False,
                            "manual_name": False,
                            "manual_partner_id": False,
                            "manual_line_id": False,
                            "manual_move_id": False,
                            "manual_move_type": False,
                            "manual_kind": False,
                            "manual_original_amount": False,
                            "manual_currency_id": False,
                            "analytic_distribution": False,
                        }
                    )
                    continue
                else:
                    self.manual_account_id = line["account_id"][0]
                    self.manual_amount = line["amount"]
                    self.manual_currency_id = line["currency_id"]
                    self.manual_name = line["name"]
                    self.manual_partner_id = (
                        line.get("partner_id") and line["partner_id"][0]
                    )
                    self.manual_line_id = line["id"]
                    self.analytic_distribution = line.get("analytic_distribution", {})
                    if self.manual_line_id:
                        self.manual_move_id = self.manual_line_id.move_id
                        self.manual_move_type = self.manual_line_id.move_id.move_type
                    self.manual_kind = line["kind"]
                    self.manual_original_amount = line.get("original_amount", 0.0)
            new_data.append(line)
        self.reconcile_data_info = self._recompute_suspense_line(
            new_data,
            self.reconcile_data_info["reconcile_auxiliary_id"],
            self.manual_reference,
        )
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    @api.onchange(
        "manual_account_id",
        "manual_partner_id",
        "manual_name",
        "manual_amount",
        "analytic_distribution",
    )
    def _onchange_manual_reconcile_vals(self):
        self.ensure_one()
        data = self.reconcile_data_info.get("data", [])
        new_data = []
        for line in data:
            if line["reference"] == self.manual_reference:
                if self._check_line_changed(line):
                    line.update(
                        {
                            "name": self.manual_name,
                            "partner_id": self.manual_partner_id
                            and self.manual_partner_id.name_get()[0]
                            or (False, self.partner_name),
                            "account_id": self.manual_account_id.name_get()[0]
                            if self.manual_account_id
                            else [False, _("Undefined")],
                            "amount": self.manual_amount,
                            "credit": -self.manual_amount
                            if self.manual_amount < 0
                            else 0.0,
                            "debit": self.manual_amount
                            if self.manual_amount > 0
                            else 0.0,
                            "analytic_distribution": self.analytic_distribution,
                            "kind": line["kind"]
                            if line["kind"] != "suspense"
                            else "other",
                        }
                    )
                    if line["kind"] == "liquidity":
                        self._update_move_partner()
            new_data.append(line)
        self.reconcile_data_info = self._recompute_suspense_line(
            new_data,
            self.reconcile_data_info["reconcile_auxiliary_id"],
            self.manual_reference,
        )
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    def _update_move_partner(self):
        if self.partner_id == self.manual_partner_id:
            return
        self.partner_id = self.manual_partner_id

    @api.depends("reconcile_data")
    def _compute_reconcile_data_info(self):
        for record in self:
            if record.reconcile_data:
                record.reconcile_data_info = record.reconcile_data
            else:
                record.reconcile_data_info = record._default_reconcile_data(
                    from_unreconcile=record.is_reconciled
                )
            record.can_reconcile = record.reconcile_data_info.get(
                "can_reconcile", False
            )

    def action_show_move(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_journal_line"
        )
        action.update(
            {"res_id": self.move_id.id, "views": [[False, "form"]], "view_mode": "form"}
        )
        return action

    def _inverse_reconcile_data_info(self):
        for record in self:
            record.reconcile_data = record.reconcile_data_info

    def _reconcile_data_by_model(self, data, reconcile_model, reconcile_auxiliary_id):
        new_data = []
        liquidity_amount = 0.0
        for line_data in data:
            if line_data["kind"] == "suspense":
                continue
            new_data.append(line_data)
            liquidity_amount += line_data["amount"]
        for line in reconcile_model._get_write_off_move_lines_dict(
            -liquidity_amount, self._retrieve_partner()
        ):
            new_line = line.copy()
            amount = line.get("balance")
            if self.foreign_currency_id:
                amount = self.foreign_currency_id.compute(
                    amount, self.journal_id.currency_id or self.company_currency_id
                )
            new_line.update(
                {
                    "reference": "reconcile_auxiliary;%s" % reconcile_auxiliary_id,
                    "id": False,
                    "amount": amount,
                    "debit": amount if amount > 0 else 0,
                    "credit": -amount if amount < 0 else 0,
                    "kind": "other",
                    "account_id": self.env["account.account"]
                    .browse(line["account_id"])
                    .name_get()[0],
                    "date": fields.Date.to_string(self.date),
                    "line_currency_id": self.company_id.currency_id.id,
                    "currency_id": self.company_id.currency_id.id,
                    "currency_amount": amount,
                }
            )
            reconcile_auxiliary_id += 1
            if line.get("partner_id"):
                new_line["partner_id"] = (
                    self.env["res.partner"].browse(line["partner_id"]).name_get()[0]
                )
            new_data.append(new_line)
        return new_data, reconcile_auxiliary_id

    def _compute_exchange_rate(
        self, data, reconcile_auxiliary_id, exchange_recompute=False
    ):
        if not exchange_recompute:
            return reconcile_auxiliary_id
        foreign_currency = (
            self.currency_id != self.company_id.currency_id
            or self.foreign_currency_id
            or any(line["currency_id"] != line["line_currency_id"] for line in data)
        )
        if not foreign_currency or self.is_reconciled:
            return reconcile_auxiliary_id
        currency = self.journal_id.currency_id or self.company_id.currency_id
        amount = sum(d.get("net_amount", 0) for d in data)
        if not currency.is_zero(amount):
            account = self.company_id.expense_currency_exchange_account_id
            if amount > 0:
                account = self.company_id.income_currency_exchange_account_id
            data.append(
                {
                    "reference": "reconcile_auxiliary;%s" % reconcile_auxiliary_id,
                    "id": False,
                    "account_id": account.name_get()[0],
                    "partner_id": False,
                    "date": fields.Date.to_string(self.date),
                    "name": self.payment_ref or self.name,
                    "amount": -amount,
                    "net_amount": -amount,
                    "credit": amount if amount > 0 else 0.0,
                    "debit": -amount if amount < 0 else 0.0,
                    "kind": "other",
                    "currency_id": self.currency_id.id,
                    "line_currency_id": self.currency_id.id,
                    "currency_amount": -amount,
                }
            )
            reconcile_auxiliary_id += 1
        return reconcile_auxiliary_id

    def _default_reconcile_data(self, from_unreconcile=False):
        liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()
        data = [self._get_reconcile_line(line, "liquidity") for line in liquidity_lines]
        reconcile_auxiliary_id = 1
        if not from_unreconcile:
            res = (
                self.env["account.reconcile.model"]
                .search(
                    [("rule_type", "in", ["invoice_matching", "writeoff_suggestion"])]
                )
                ._apply_rules(self, self._retrieve_partner())
            )
            if res and res.get("status", "") == "write_off":
                return self._recompute_suspense_line(
                    *self._reconcile_data_by_model(
                        data, res["model"], reconcile_auxiliary_id
                    ),
                    self.manual_reference,
                    exchange_recompute=True
                )
            elif res and res.get("amls"):
                amount = self.amount_total_signed
                for line in res.get("amls", []):
                    line_data = self._get_reconcile_line(
                        line, "other", is_counterpart=True, max_amount=amount
                    )
                    amount -= line_data.get("amount")
                    data.append(line_data)
                return self._recompute_suspense_line(
                    data,
                    reconcile_auxiliary_id,
                    self.manual_reference,
                    exchange_recompute=True,
                )
        return self._recompute_suspense_line(
            data
            + [
                self._get_reconcile_line(
                    line, "other", from_unreconcile=from_unreconcile
                )
                for line in other_lines
            ],
            reconcile_auxiliary_id,
            self.manual_reference,
        )

    def clean_reconcile(self):
        self.reconcile_data_info = self._default_reconcile_data()
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    def reconcile_bank_line(self):
        self.ensure_one()
        self.reconcile_mode = self.journal_id.reconcile_mode
        result = getattr(self, "_reconcile_bank_line_%s" % self.reconcile_mode)(
            self.reconcile_data_info["data"]
        )
        self.reconcile_data_info = False
        return result

    def _reconcile_bank_line_edit(self, data):
        _liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()
        lines_to_remove = [(2, line.id) for line in suspense_lines + other_lines]

        # Cleanup previous lines.
        move = self.move_id
        container = {"records": move, "self": move}
        to_reconcile = []
        with move._check_balanced(container):
            move.with_context(
                skip_account_move_synchronization=True,
                force_delete=True,
                skip_invoice_sync=True,
            ).write(
                {
                    "line_ids": lines_to_remove,
                }
            )
            for line_vals in data:
                if line_vals["kind"] == "liquidity":
                    continue
                line = (
                    self.env["account.move.line"]
                    .with_context(
                        check_move_validity=False,
                        skip_sync_invoice=True,
                        skip_invoice_sync=True,
                    )
                    .create(self._reconcile_move_line_vals(line_vals))
                )
                if line_vals.get("counterpart_line_id"):
                    to_reconcile.append(
                        self.env["account.move.line"].browse(
                            line_vals.get("counterpart_line_id")
                        )
                        + line
                    )
        for reconcile_items in to_reconcile:
            reconcile_items.reconcile()

    def _reconcile_bank_line_keep_move_vals(self):
        return {
            "journal_id": self.journal_id.id,
        }

    def _reconcile_bank_line_keep(self, data):
        move = (
            self.env["account.move"]
            .with_context(skip_invoice_sync=True)
            .create(self._reconcile_bank_line_keep_move_vals())
        )
        _liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()
        container = {"records": move, "self": move}
        to_reconcile = defaultdict(lambda: self.env["account.move.line"])
        with move._check_balanced(container):
            for line in suspense_lines | other_lines:
                to_reconcile[line.account_id.id] |= line
                line_data = line.with_context(
                    active_test=False,
                    include_business_fields=True,
                ).copy_data({"move_id": move.id})[0]
                to_reconcile[line.account_id.id] |= (
                    self.env["account.move.line"]
                    .with_context(
                        check_move_validity=False,
                        skip_sync_invoice=True,
                        skip_invoice_sync=True,
                    )
                    .create(line_data)
                )
            move.write(
                {
                    "line_ids": [
                        Command.update(
                            line.id,
                            {
                                "balance": -line.balance,
                                "amount_currency": -line.amount_currency,
                            },
                        )
                        for line in move.line_ids
                        if line.move_id.move_type == "entry"
                        or line.display_type == "cogs"
                    ]
                }
            )
            for line_vals in data:
                if line_vals["kind"] == "liquidity":
                    continue
                if line_vals["kind"] == "suspense":
                    raise UserError(_("No supense lines are allowed when reconciling"))
                line = (
                    self.env["account.move.line"]
                    .with_context(check_move_validity=False, skip_invoice_sync=True)
                    .create(self._reconcile_move_line_vals(line_vals, move.id))
                )
                if line_vals.get("counterpart_line_id") and line.account_id.reconcile:
                    to_reconcile[line.account_id.id] |= (
                        self.env["account.move.line"].browse(
                            line_vals.get("counterpart_line_id")
                        )
                        | line
                    )
            move.invalidate_recordset()
        move._post()
        for _account, lines in to_reconcile.items():
            lines.reconcile()

    def unreconcile_bank_line(self):
        self.ensure_one()
        return getattr(
            self, "_unreconcile_bank_line_%s" % (self.reconcile_mode or "edit")
        )()

    def _unreconcile_bank_line_edit(self):
        self.reconcile_data_info = self._default_reconcile_data(from_unreconcile=True)
        self.action_undo_reconciliation()

    def _unreconcile_bank_line_keep(self):
        raise UserError(_("Keep suspense move lines mode cannot be unreconciled"))

    def _reconcile_move_line_vals(self, line, move_id=False):
        return {
            "move_id": move_id or self.move_id.id,
            "account_id": line["account_id"][0],
            "partner_id": line.get("partner_id") and line["partner_id"][0],
            "credit": line["credit"],
            "debit": line["debit"],
            "tax_ids": line.get("tax_ids", []),
            "tax_tag_ids": line.get("tax_tag_ids", []),
            "group_tax_id": line.get("group_tax_id"),
            "tax_repartition_line_id": line.get("tax_repartition_line_id"),
            "analytic_distribution": line.get("analytic_distribution"),
            "name": line.get("name"),
            "reconcile_model_id": line.get("reconcile_model_id"),
        }

    @api.model_create_multi
    def create(self, mvals):
        result = super().create(mvals)
        models = self.env["account.reconcile.model"].search(
            [
                ("rule_type", "in", ["invoice_matching", "writeoff_suggestion"]),
                ("auto_reconcile", "=", True),
            ]
        )
        for record in result:
            res = models._apply_rules(record, record._retrieve_partner())
            if not res:
                continue
            liquidity_lines, suspense_lines, other_lines = record._seek_for_lines()
            data = [
                record._get_reconcile_line(line, "liquidity")
                for line in liquidity_lines
            ]
            reconcile_auxiliary_id = 1
            if res.get("status", "") == "write_off":
                data = record._recompute_suspense_line(
                    *record._reconcile_data_by_model(
                        data, res["model"], reconcile_auxiliary_id
                    ),
                    self.manual_reference,
                    exchange_recompute=True
                )
            elif res.get("amls"):
                amount = self.amount
                for line in res.get("amls", []):
                    line_data = record._get_reconcile_line(
                        line, "other", is_counterpart=True, max_amount=amount
                    )
                    amount -= line_data.get("amount")
                    data.append(line_data)
                data = record._recompute_suspense_line(
                    data,
                    reconcile_auxiliary_id,
                    self.manual_reference,
                    exchange_recompute=True,
                )
            if not data.get("can_reconcile"):
                continue
            getattr(
                record, "_reconcile_bank_line_%s" % record.journal_id.reconcile_mode
            )(data["data"])
        return result

    def button_manual_reference_full_paid(self):
        self.ensure_one()
        if not self.reconcile_data_info["manual_reference"]:
            return
        manual_reference = self.reconcile_data_info["manual_reference"]
        data = self.reconcile_data_info.get("data", [])
        new_data = []
        reconcile_auxiliary_id = self.reconcile_data_info["reconcile_auxiliary_id"]
        for line in data:
            if line["reference"] == manual_reference and line.get("id"):
                total_amount = -line["amount"] + line["original_amount_unsigned"]
                original_amount = line["original_amount_unsigned"]
                new_data.append(
                    self._get_reconcile_line(
                        self.env["account.move.line"].browse(line["id"]),
                        "other",
                        is_counterpart=True,
                        max_amount=original_amount,
                    )
                )
                new_data.append(
                    {
                        "reference": "reconcile_auxiliary;%s" % reconcile_auxiliary_id,
                        "id": False,
                        "account_id": line["account_id"],
                        "partner_id": line.get("partner_id"),
                        "date": line["date"],
                        "name": line["name"],
                        "amount": -total_amount,
                        "credit": total_amount if total_amount > 0 else 0.0,
                        "debit": -total_amount if total_amount < 0 else 0.0,
                        "kind": "other",
                        "currency_id": line["currency_id"],
                        "line_currency_id": line["currency_id"],
                        "currency_amount": -total_amount,
                    }
                )
                reconcile_auxiliary_id += 1
            else:
                new_data.append(line)
        self.reconcile_data_info = self._recompute_suspense_line(
            new_data,
            reconcile_auxiliary_id,
            self.manual_reference,
            exchange_recompute=True,
        )
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    def action_to_check(self):
        self.ensure_one()
        self.move_id.to_check = True
        if self.can_reconcile and self.journal_id.reconcile_mode == "edit":
            self.reconcile_bank_line()

    def action_checked(self):
        self.ensure_one()
        self.move_id.to_check = False

    def _get_reconcile_line(
        self, line, kind, is_counterpart=False, max_amount=False, from_unreconcile=False
    ):
        vals = super()._get_reconcile_line(
            line,
            kind,
            is_counterpart=is_counterpart,
            max_amount=max_amount,
            from_unreconcile=from_unreconcile,
        )
        if vals["partner_id"] is False:
            vals["partner_id"] = (False, self.partner_name)
        return vals
