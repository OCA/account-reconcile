# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import Command, fields, models
from odoo.tools import SQL, Query


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    search_journal_id = fields.Many2one(
        "account.journal",
        string="Applies on Journal",
        store=False,
        search="_search_search_journal_id",
    )

    def _search_search_journal_id(self, operator, value):
        if operator not in ["=", "in"]:
            return []
        return [
            "|",
            ("match_journal_ids", operator, value),
            ("match_journal_ids", "=", False),
        ]

    def _get_rules(self, bank_statement_lines, trigger="auto_reconcile"):
        if not bank_statement_lines:
            return {}
        bank_statement_lines.flush_recordset()
        self.env["account.reconcile.model"].flush_model()
        query = self._get_rules_query(bank_statement_lines, trigger=trigger)
        self.env.cr.execute(
            query.select(
                SQL.identifier(self._table, "id"),
                SQL.identifier(bank_statement_lines._table, "id"),
            )
        )
        data = {}
        for model_id, line_id in self.env.cr.fetchall():
            data[line_id] = data.get(line_id, []) + [model_id]
        return data

    def _get_rules_query(self, bank_statement_lines, trigger="auto_reconcile"):
        """
        The idea here is to define the SQL to get all possible rules that apply to
        some statement lines
        We will return a query object that we could edit later on to add extra
        things on the query.
        By default it will get all the rules that match
        """
        query = Query(
            self.env, bank_statement_lines._table, bank_statement_lines._table_sql
        )
        query.add_join(
            "JOIN",
            bank_statement_lines.move_id._table,
            bank_statement_lines.move_id._table,
            SQL(
                "%s=%s",
                SQL.identifier(bank_statement_lines._table, "move_id"),
                SQL.identifier(bank_statement_lines.move_id._table, "id"),
            ),
        )
        query.add_join("LEFT JOIN", self._table, self._table, SQL("TRUE"))
        query.add_join(
            "LEFT JOIN",
            "account_journal_account_reconcile_model_rel",
            "account_journal_account_reconcile_model_rel",
            SQL(
                "%s = %s",
                SQL.identifier(self._table, "id"),
                SQL.identifier(
                    "account_journal_account_reconcile_model_rel",
                    "account_reconcile_model_id",
                ),
            ),
        )
        query.add_join(
            "LEFT JOIN",
            "account_reconcile_model_res_partner_rel",
            "account_reconcile_model_res_partner_rel",
            SQL(
                "%s = %s",
                SQL.identifier(self._table, "id"),
                SQL.identifier(
                    "account_reconcile_model_res_partner_rel",
                    "account_reconcile_model_id",
                ),
            ),
        )
        query.add_where(
            SQL(
                "(%(relation)s IS NULL OR %(relation)s = %(move_field)s)",
                relation=SQL.identifier(
                    "account_journal_account_reconcile_model_rel", "account_journal_id"
                ),
                move_field=SQL.identifier(
                    bank_statement_lines.move_id._table, "journal_id"
                ),
            )
        )
        query.add_where(
            SQL(
                "(%(relation)s IS NULL OR %(relation)s = %(move_field)s)",
                relation=SQL.identifier(
                    "account_reconcile_model_res_partner_rel", "res_partner_id"
                ),
                move_field=SQL.identifier(
                    bank_statement_lines.move_id._table, "partner_id"
                ),
            )
        )
        query.add_where(
            SQL(
                """(%(match_field)s IS NULL OR CASE %(match_field)s
                    WHEN 'lower' THEN %(line_amount)s <= %(max_amount)s
                    WHEN 'greater' THEN %(line_amount)s >= %(min_amount)s
                    WHEN 'between' THEN %(line_amount)s
                        BETWEEN %(max_amount)s AND %(min_amount)s
                    ELSE TRUE
                END)""",
                match_field=SQL.identifier(self._table, "match_amount"),
                line_amount=SQL.identifier(bank_statement_lines._table, "amount"),
                max_amount=SQL.identifier(self._table, "match_amount_max"),
                min_amount=SQL.identifier(self._table, "match_amount_min"),
            )
        )
        query.add_where(
            SQL(
                """(%(match_field)s IS NULL OR
        CASE %(match_field)s
        WHEN 'contains' THEN (
            (%(payment_ref)s is not null
                AND %(payment_ref)s::TEXT  ILIKE '%%' || %(match_label)s || '%%')
            OR (%(transaction)s is not null
                AND %(transaction)s::TEXT  ILIKE '%%' || %(match_label)s || '%%')
            OR (%(narration)s is not null
                AND %(narration)s::TEXT  ILIKE '%%' || %(match_label)s || '%%'))
        WHEN 'not_contains' THEN NOT (
            (%(payment_ref)s is not null
                AND %(payment_ref)s::TEXT  ILIKE '%%' || %(match_label)s || '%%')
            OR (%(transaction)s is not null
                AND %(transaction)s::TEXT  ILIKE '%%' || %(match_label)s || '%%')
            OR (%(narration)s is not null
                AND %(narration)s::TEXT  ILIKE '%%' || %(match_label)s || '%%'))
        WHEN 'match_regex' THEN (
            (%(payment_ref)s is not null
                AND %(payment_ref)s::TEXT  ~* %(match_label)s )
            OR (%(transaction)s is not null
                AND %(transaction)s::TEXT  ~* %(match_label)s )
            OR (%(narration)s is not null
                AND %(narration)s::TEXT  ~* %(match_label)s ))
        ELSE TRUE
        END)""",
                match_field=SQL.identifier(self._table, "match_label"),
                match_label=SQL.identifier(self._table, "match_label_param"),
                payment_ref=SQL.identifier(bank_statement_lines._table, "payment_ref"),
                transaction=SQL.identifier(
                    bank_statement_lines._table, "transaction_details"
                ),
                narration=SQL.identifier(
                    bank_statement_lines.move_id._table, "narration"
                ),
            )
        )
        query.add_where(SQL.identifier(self._table, "can_be_proposed"))
        query.add_where(
            SQL(
                "%s = %s",
                SQL.identifier(self._table, "company_id"),
                SQL.identifier(bank_statement_lines._table, "company_id"),
            )
        )
        query.add_where(SQL("%s", SQL.identifier(self._table, "active")))
        query.add_where(
            SQL(
                "%s IN %s",
                SQL.identifier(bank_statement_lines._table, "id"),
                tuple(bank_statement_lines.ids),
            )
        )
        query.add_where(SQL("%s = %s", SQL.identifier(self._table, "trigger"), trigger))
        query.order = SQL.identifier(self._table, "sequence").code
        return query

    # After this code comes from odoo old versions. It is necessary to remove it...

    def _get_taxes_move_lines_dict(self, tax, base_line_dict):
        """Get move.lines dict (to be passed to the create()) corresponding to a tax.
        :param tax: An account.tax record.
        :param base_line_dict: A dict representing the move.line containing the base
          amount.
        :return: A list of dict representing move.lines to be created corresponding to
          the tax.
        """
        self.ensure_one()
        balance = base_line_dict["balance"]

        tax_type = tax.type_tax_use
        is_refund = (tax_type == "sale" and balance < 0) or (
            tax_type == "purchase" and balance > 0
        )

        res = tax.compute_all(balance, is_refund=is_refund)

        new_aml_dicts = []
        for tax_res in res["taxes"]:
            tax = self.env["account.tax"].browse(tax_res["id"])
            balance = tax_res["amount"]
            name = " ".join(
                [x for x in [base_line_dict.get("name", ""), tax_res["name"]] if x]
            )
            new_aml_dicts.append(
                {
                    "account_id": tax_res["account_id"] or base_line_dict["account_id"],
                    "journal_id": base_line_dict.get("journal_id", False),
                    "name": name,
                    "partner_id": base_line_dict.get("partner_id"),
                    "balance": balance,
                    "debit": balance > 0 and balance or 0,
                    "credit": balance < 0 and -balance or 0,
                    "analytic_distribution": tax.analytic
                    and base_line_dict["analytic_distribution"],
                    "tax_repartition_line_id": tax_res["tax_repartition_line_id"],
                    "tax_ids": [(6, 0, tax_res["tax_ids"])],
                    "tax_tag_ids": [(6, 0, tax_res["tag_ids"])],
                    "group_tax_id": tax_res["group"].id if tax_res["group"] else False,
                    "currency_id": False,
                    "reconcile_model_id": self.id,
                }
            )

            # Handle price included taxes.
            base_balance = tax_res["base"]
            base_line_dict.update(
                {
                    "balance": base_balance,
                    "debit": base_balance > 0 and base_balance or 0,
                    "credit": base_balance < 0 and -base_balance or 0,
                }
            )

        base_line_dict["tax_tag_ids"] = [(6, 0, res["base_tags"])]
        return new_aml_dicts

    def _get_write_off_move_lines_dict(
        self, residual_balance, partner_id, statement_line
    ):
        self.ensure_one()
        currency = self.company_id.currency_id
        lines_vals_list = []
        for line in self.line_ids:
            balance = line._get_amount_from_line(
                residual_balance, statement_line, currency
            )
            if currency.is_zero(balance):
                continue
            writeoff_line = line._get_write_off_move_line_dict(balance, currency)
            lines_vals_list.append(writeoff_line)
            residual_balance -= balance
            if line.tax_ids:
                taxes = line.tax_ids
                detected_fiscal_position = self.env[
                    "account.fiscal.position"
                ]._get_fiscal_position(self.env["res.partner"].browse(partner_id))
                if detected_fiscal_position:
                    taxes = detected_fiscal_position.map_tax(taxes)
                writeoff_line["tax_ids"] += [Command.set(taxes.ids)]
                # Multiple taxes with force_tax_included results in wrong computation,
                # so we only allow to set the force_tax_included field if we have one
                # tax selected
                tax_vals_list = self._get_taxes_move_lines_dict(taxes, writeoff_line)
                lines_vals_list += tax_vals_list
                for tax_line in tax_vals_list:
                    residual_balance -= tax_line["balance"]

        return lines_vals_list


class AccountReconcileModelLine(models.Model):
    _inherit = "account.reconcile.model.line"

    def _get_write_off_move_line_dict(self, balance, currency):
        self.ensure_one()
        return {
            "name": self.label,
            "balance": balance,
            "debit": balance > 0 and balance or 0,
            "credit": balance < 0 and -balance or 0,
            "account_id": self.account_id.id,
            "currency_id": currency.id,
            "analytic_distribution": self.analytic_distribution,
            "reconcile_model_id": self.model_id.id,
            "tax_ids": [],
        }

    def _get_amount_from_line(self, residual_balance, statement_line, currency):
        if self.amount_type == "percentage":
            return currency.round(residual_balance * (self.amount / 100.0))
        if self.amount_type == "fixed":
            return currency.round(self.amount * (1 if residual_balance > 0.0 else -1))
        if self.amount_type == "percentage_st_line":
            return currency.round(
                statement_line.amount
                * (self.amount / 100.0)
                * (1 if residual_balance > 0.0 else -1)
            )
        if self.amount_type == "regex":
            for value in (statement_line.payment_ref, statement_line.narration):
                if not value:
                    continue
                if m := re.findall(self.amount_string, value or ""):
                    extracted_amount = 0.0
                    # We find the last separator, split by it and concatenate the
                    # parts to get the correct amount
                    if decimal := re.match(r"^([\d\,\.]+)[\.\,](\d*)$", m[0]):
                        extracted_amount = float(
                            decimal.group(1).replace(",", "").replace(".", "")
                            + "."
                            + decimal.group(2)
                        )
                    elif decimal := re.match(r"^(\d+)$", m[0]):
                        # If it is a full number, consider it as the amount
                        # without decimals
                        extracted_amount = float(decimal.group(1))
                    return currency.round(
                        extracted_amount * (1 if residual_balance > 0.0 else -1)
                    )
        return 0.0
