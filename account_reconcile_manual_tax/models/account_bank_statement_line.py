# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    manual_tax_ids = fields.Many2many(
        "account.tax",
        relation="account_bank_statement_line_manual_tax_ids_rel",
        check_company=True,
        string="Taxes",
        domain=[("price_include", "=", True)],
    )

    @api.onchange(
        "manual_tax_ids",
    )
    def _onchange_manual_tax_ids(self):
        return super()._onchange_manual_reconcile_vals()

    def _check_line_changed(self, line):
        changed = set(line.get("tax_ids") or []) != {
            tax.id.origin for tax in self.manual_tax_ids
        }
        return changed or super()._check_line_changed(line)

    def _get_manual_delete_vals(self):
        return dict(
            super()._get_manual_delete_vals(), manual_tax_ids=[fields.Command.set([])]
        )

    def _process_manual_reconcile_from_line(self, line):
        self.manual_tax_ids = line.get("tax_ids")
        return super()._process_manual_reconcile_from_line(line)

    def _get_manual_reconcile_vals(self):
        return dict(
            super()._get_manual_reconcile_vals(),
            tax_ids=[tax.id.origin for tax in self.manual_tax_ids],
        )

    def _reconcile_move_line_vals(self, line, move_id=False):
        return dict(
            super()._reconcile_move_line_vals(line, move_id=move_id),
            tax_repartition_line_id=line.get("tax_repartition_line_id"),
        )

    def _recompute_suspense_line(self, data, reconcile_auxiliary_id, manual_reference):
        result = super()._recompute_suspense_line(
            data, reconcile_auxiliary_id, manual_reference
        )
        if self.manual_model_id:
            return result
        i = 0
        lines = result.get("data", [])
        while i < len(lines):
            line = lines[i]
            if line.get("reconcile_model_id"):
                i += 1
                continue
            new_lines = []
            if line["kind"] == "tax":
                lines[i : i + 1] = []
                i -= 1
                continue
            if line.get("tax_ids"):
                new_lines = self._recompute_suspense_line_manual_tax(line)
            elif line.get("amount_before_taxes"):
                line["amount"] = line.pop("amount_before_taxes")
                line["debit"] = line["debit"] and line["amount"]
                line["credit"] = line["credit"] and line["amount"]
            lines[i + 1 : i + 1] = new_lines
            i += len(new_lines) + 1

        return result

    def _recompute_suspense_line_manual_tax(self, line):
        AccountMoveLine = self.env["account.move.line"]
        new_line = AccountMoveLine.new(
            {
                key: value
                for key, value in line.items()
                if key in AccountMoveLine._fields
            }
        )
        sign = 1 if line["amount"] > 0 else -1
        taxes = new_line.tax_ids.compute_all(
            line.get("amount_before_taxes", sign * line["amount"]),
            handle_price_include=True,
        )

        line.setdefault("amount_before_taxes", line["amount"])
        line["amount"] = sign * taxes["total_excluded"]
        line["credit"] = line["credit"] and taxes["total_excluded"] or line["credit"]
        line["debit"] = line["debit"] and taxes["total_excluded"] or line["debit"]

        return [
            {
                "reference": line["reference"] + f"-{sequence}",
                "id": False,
                "account_id": (tax["account_id"] or self.account_id.id, tax["name"]),
                "partner_id": line.get("partner_id"),
                "date": line["date"],
                "name": tax["name"],
                "amount": sign * tax["amount"],
                "credit": line["credit"] and tax["amount"],
                "debit": line["debit"] and tax["amount"],
                "kind": "tax",
                "currency_id": line["currency_id"],
                "line_currency_id": line["line_currency_id"],
                "currency_amount": 0,
                "tax_repartition_line_id": tax["tax_repartition_line_id"].origin,
                "tax_tag_ids": tax["tag_ids"],
            }
            for sequence, tax in enumerate(taxes["taxes"])
        ]
