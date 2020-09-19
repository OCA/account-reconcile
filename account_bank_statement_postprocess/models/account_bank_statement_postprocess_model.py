# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from decimal import Decimal, ROUND_HALF_UP
import re


class AccountBankStatementPostprocessModel(models.Model):
    _name = "account.bank.statement.postprocess.model"
    _description = "Account Bank Statement Postprocess Model"
    _order = "sequence, id"

    sequence = fields.Integer(
        required=True,
        default=10,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    postprocess_type = fields.Selection(
        string="Type",
        selection=lambda self: self._selection_postprocess_type(),
        required=True,
        default=lambda self: self._selection_postprocess_type()[0][0],
        help="Type of the postprocess model",
    )
    match_journal_ids = fields.Many2many(
        string="Journals",
        comodel_name="account.journal",
        domain=[("type", "in", ("bank", "cash"))],
        help=(
            "The postprocess model will only be applicable to records from the "
            "selected journals, if specified."
        ),
    )
    match_transaction_type = fields.Selection(
        string="Transaction Type",
        selection=[
            ("debit", _("Debit")),
            ("credit", _("Credit")),
            ("any", _("Any")),
        ],
        default="any",
        required=True,
        help="Type of the transaction to apply postprocess matching to.",
    )
    match_field = fields.Selection(
        string="Field",
        selection=lambda self: self._selection_match_field(),
        required=True,
        help="Field of the transaction record to be used for postprocess matching.",
    )
    match_regexp = fields.Char(
        string="Expression",
        required=True,
        help=(
            "Regular expression used to extract information from the field of "
            "the transaction record. See help for details."
        ),
    )
    match_help = fields.Html(
        string="Help",
        compute="_compute_match_help",
    )
    apply_on_import = fields.Boolean(
        string="Apply on Import",
        help=(
            "If enabled, the model will be applied automatically on statement "
            "import."
        ),
    )
    allow_recursion = fields.Boolean(
        string="Allow Recursion",
        help=(
            "For models that create new statement lines: if enabled, new lines"
            "are going to be post-processed as well."
        ),
    )
    is_other_field_supported = fields.Boolean(
        string="Is \"Other Field\" supported",
        compute="_compute_is_other_field_supported",
    )
    other_field = fields.Selection(
        string="Other Field",
        selection=lambda self: self._selection_other_field(),
        help="See postprocess model help.",
    )
    is_other_value_supported = fields.Boolean(
        string="Is \"Other Value\" supported",
        compute="_compute_is_other_value_supported",
    )
    other_value = fields.Char(
        string="Other Value",
    )

    @api.model
    def _selection_postprocess_type(self):
        return [
            ("extract_fee", _("Extract fee")),
            ("multi_currency", _("Multi-currency")),
            ("multi_currency_with_fee", _("Multi-currency (fee included)")),
            ("trim_field", _("Trim field")),
            ("append_field", _("Append field")),
            ("merge_per_statement", _("Merge per statement")),
            ("delete", _("Delete")),
        ]

    @api.model
    def _selection_match_field(self):
        fields = self.env["account.bank.statement.line"].fields_get().items()
        return [
            (field, definition.get("string"))
            for field, definition in fields
            if self._is_match_field_supported(field, definition)
        ]

    @api.model
    def _is_match_field_supported(self, field, definition):
        return definition["type"] in ["char", "text"]

    @api.model
    def _selection_other_field(self):
        fields = self.env["account.bank.statement.line"].fields_get().items()
        return [
            (field, definition.get("string"))
            for field, definition in fields
            if self._is_other_field_valid(field, definition)
        ]

    @api.model
    def _is_other_field_valid(self, field, definition):
        return definition["type"] in ["char", "text"]

    @api.multi
    @api.depends("postprocess_type")
    def _compute_match_help(self):
        for model in self:
            model.match_help = model._get_match_help()

    @api.multi
    def _get_match_help(self):
        self.ensure_one()
        if self.postprocess_type == "extract_fee":
            return _(
                "\"Extract Fee\" model looks for the fee amount in the "
                "specified field of the transaction record. In order to "
                "extract the fee amount value, use <code>FEE</code> or "
                "<code>FEE_PERCENT</code> named group in the regular "
                "expression. Value of \"Other Value\" is formatted using "
                "named groups i.e <code>%%()s</code> for full match or "
                "<code>%%(GROUP_NAME)s</code> for a specific group value "
                "is used as a new transaction record description."
            )
        elif self.postprocess_type == "multi_currency":
            return _(
                "\"Multi-Currency\" model looks for the transaction amount "
                "expressed in the other currency in case of a multi-currency "
                "transaction record. The other currency and the amount are "
                "saved into corresponding fields of the transaction record. "
                "In order to extract the other currency code use "
                "<code>CURRENCY</code> named group and "
                "<code>AMOUNT_CURRENCY</code> for extracting the amount "
                "expressed in that currency. <code>EXCHANGE_RATE</code> can "
                "be specified to double-check amount computation."
            )
        elif self.postprocess_type == "multi_currency_with_fee":
            return _(
                "\"Multi-Currency (Fee Included)\" model looks for the "
                "transaction amount expressed in the other currency in case "
                "of a multi-currency transaction record. The other currency "
                "and the amount are saved into corresponding fields of the "
                "transaction record. This model writes off into transaction "
                "fee the remainder of the transaction. In order to extract "
                "the other currency code use <code>CURRENCY</code> named "
                "group and <code>AMOUNT_CURRENCY</code> for extracting the "
                "amount expressed in that currency. "
                "<code>EXCHANGE_RATE</code> is used to compute remainder of "
                "the transaction. Value of \"Other Value\" is formatted using "
                "named groups i.e <code>%%()s</code> for full match or "
                "<code>%%(GROUP_NAME)s</code> for a specific group value "
                "is used as a new transaction record description."
            )
        elif self.postprocess_type == "trim_field":
            return _(
                "\"Trim Field\" model matches transactions by the value of "
                "the specified field of the transaction record and removes "
                "match from the field value using capturing groups."
            )
        elif self.postprocess_type == "append_field":
            return _(
                "\"Append Field\" model matches transactions by the value of "
                "the specified field of the transaction record and appends "
                "match using the value of the other field."
            )
        elif self.postprocess_type == "merge_per_statement":
            return _(
                "\"Merge per Statement\" model matches transactions by the "
                "value of the specified field of the transaction record and "
                "merges records that matched into a new transaction record "
                "created per statement. Value of \"Other Value\" is formatted "
                "using named groups (i.e <code>%%(GROUP_NAME)s</code>) is "
                "used as a new transaction record description."
            )
        elif self.postprocess_type == "delete":
            return _(
                "\"Delete\" model matches transactions by the value of "
                "the specified field of the transaction record and deletes "
                "records that matched."
            )

    @api.multi
    @api.depends("postprocess_type")
    def _compute_is_other_field_supported(self):
        for model in self:
            model.is_other_field_supported = model._is_other_field_supported()

    @api.multi
    def _is_other_field_supported(self):
        self.ensure_one()
        return self.postprocess_type in [
            "append_field",
        ]

    @api.multi
    @api.depends("postprocess_type")
    def _compute_is_other_value_supported(self):
        for model in self:
            model.is_other_value_supported = model._is_other_value_supported()

    @api.multi
    def _is_other_value_supported(self):
        self.ensure_one()
        return self.postprocess_type in [
            "extract_fee",
            "multi_currency_with_fee",
            "merge_per_statement",
        ]

    @api.multi
    def apply(self, lines):
        for model in self:
            regexp = re.compile(model.match_regexp, re.DOTALL | re.MULTILINE)
            for line in lines.exists():
                if model._is_applicable(line):
                    model._try_to_apply(regexp, line)

    @api.multi
    def _is_applicable(self, line):
        self.ensure_one()
        if self.match_journal_ids \
                and line.journal_id not in self.match_journal_ids:
            return False
        if self.match_transaction_type == "debit" and line.amount >= 0.0:
            return False
        if self.match_transaction_type == "credit" and line.amount <= 0.0:
            return False
        return True

    @api.multi
    def _try_to_apply(self, regexp, line):
        self.ensure_one()
        value = str(line[self.match_field])
        match = regexp.search(value)
        if match is not None:
            self._apply(line, value, match)

    @api.multi
    def _apply(self, line, value, match):
        self.ensure_one()
        if self.postprocess_type == "extract_fee":
            self._apply_extract_fee(line, value, match)
        elif self.postprocess_type == "multi_currency":
            self._apply_multi_currency(line, value, match)
        elif self.postprocess_type == "multi_currency_with_fee":
            self._apply_multi_currency_with_fee(line, value, match)
        elif self.postprocess_type == "trim_field":
            self._apply_trim_field(line, value, match)
        elif self.postprocess_type == "append_field":
            self._apply_append_field(line, value, match)
        elif self.postprocess_type == "merge_per_statement":
            self._apply_merge_per_statement(line, value, match)
        elif self.postprocess_type == "delete":
            self._apply_delete(line, value, match)

    @api.multi
    def _create_new_statement_line(self, vals):
        self.ensure_one()
        AccountBankStatementLine = self.env["account.bank.statement.line"]
        if not self.allow_recursion:
            AccountBankStatementLine = AccountBankStatementLine.with_context(
                skip_postprocess=True,
            )
        return AccountBankStatementLine.create(vals)

    @api.multi
    def _apply_extract_fee(self, line, value, match):
        self.ensure_one()
        match_groups = match.groupdict()
        if "FEE" not in match_groups and "FEE_PERCENT" not in match_groups:
            raise UserError(_(
                "\"%s\" expression is incorrect for \"Extract Fee\" model:"
                " please specify FEE or FEE_PERCENT named group."
            ))
        fee_value = match_groups.get("FEE")
        fee_percent_value = match_groups.get("FEE_PERCENT")
        if fee_value and fee_percent_value:
            raise UserError(_(
                "\"%s\" expression is incorrect for \"Extract Fee\" model:"
                " please specify only one named group: FEE or FEE_PERCENT."
            ))
        currency = line.statement_id.currency_id
        fee_amount = self._parse_decimal(
            fee_value or fee_percent_value,
            currency=currency if fee_value else None,
        )
        line_amount = Decimal(str(line.amount))
        if fee_percent_value:
            fee_amount = fee_amount * Decimal("0.01")
            fee_amount = self._round_decimal(
                line_amount * fee_amount,
                currency
            )
        fee_amount = fee_amount.copy_sign(line_amount)

        fee_line = self._create_new_statement_line({
            "name": (self.other_value or _("Extracted Fee: %()s")) % {
                **match_groups,
                "": line.name,
            },
            "date": line.date,
            "amount": str(fee_amount),
            "statement_id": line.statement_id.id,
            "sequence": line.sequence,
        })
        line.amount = line.amount - fee_line.amount

    @api.multi
    def _apply_multi_currency(self, line, value, match):
        self.ensure_one()
        match_groups = match.groupdict()
        if "CURRENCY" not in match_groups \
                or "AMOUNT_CURRENCY" not in match_groups:
            raise UserError(_(
                "\"%s\" expression is incorrect for \"Multi-Currency\" "
                "model: please specify CURRENCY and AMOUNT_CURRENCY named "
                "groups. Optionally, use EXCHANGE_RATE."
            ))
        currency_code = match_groups.get("CURRENCY")
        amount_currency_value = match_groups.get("AMOUNT_CURRENCY")

        currency = self.env["res.currency"].search(
            [("name", "=ilike", currency_code)]
        )
        if not currency:
            raise UserError(_(
                "Currency with code \"%s\" does not exist or inactive"
            ) % (
                currency_code,
            ))

        line_amount = Decimal(str(line.amount))
        amount_currency = self._parse_decimal(
            amount_currency_value,
            currency=currency,
        )
        amount_currency = amount_currency.copy_sign(line_amount)

        exchange_rate_value = match_groups.get("EXCHANGE_RATE")
        if exchange_rate_value:
            exchange_rate = self._parse_decimal(
                exchange_rate_value
            )
            computed_amount_currency = self._round_decimal(
                line_amount / exchange_rate,
                currency
            )
            if computed_amount_currency != amount_currency:
                raise UserError(_(
                    "Amount computed using reference exchange rate (%s) "
                    "differs from the amount parsed from the field (%s)."
                ) % (
                    computed_amount_currency,
                    amount_currency,
                ))
        line.write({
            "amount_currency": str(amount_currency),
            "currency_id": currency.id,
        })

    @api.multi
    def _apply_multi_currency_with_fee(self, line, value, match):
        self.ensure_one()
        match_groups = match.groupdict()
        if "CURRENCY" not in match_groups \
                or "AMOUNT_CURRENCY" not in match_groups \
                or "EXCHANGE_RATE" not in match_groups:
            raise UserError(_(
                "\"%s\" expression is incorrect for \"Multi-Currency (Fee "
                "Included)\" model: please specify CURRENCY, "
                "AMOUNT_CURRENCY, and EXCHANGE_RATE named groups."
            ))
        currency_code = match_groups.get("CURRENCY")
        amount_currency_value = match_groups.get("AMOUNT_CURRENCY")
        exchange_rate_value = match_groups.get("EXCHANGE_RATE")

        currency = self.env["res.currency"].search(
            [("name", "=ilike", currency_code)]
        )
        if not currency:
            raise UserError(_(
                "Currency with code \"%s\" does not exist or inactive"
            ) % (
                currency_code,
            ))

        total_amount = Decimal(str(line.amount))
        exchange_rate = self._parse_decimal(exchange_rate_value)

        amount_currency = self._parse_decimal(
            amount_currency_value,
            currency=currency,
        )
        amount_currency = amount_currency.copy_sign(total_amount)
        line_amount = self._round_decimal(
            amount_currency * exchange_rate,
            line.statement_id.currency_id
        )
        fee_amount = total_amount - line_amount

        self._create_new_statement_line({
            "name": (self.other_value or _("Extracted Fee: %()s")) % {
                **match_groups,
                "": line.name,
            },
            "date": line.date,
            "amount": str(fee_amount),
            "statement_id": line.statement_id.id,
            "sequence": line.sequence,
        })
        line.write({
            "amount": str(line_amount),
            "amount_currency": str(amount_currency),
            "currency_id": currency.id,
        })

    @api.multi
    def _apply_trim_field(self, line, value, match):
        self.ensure_one()
        if match.groups():
            for group in match.groups():
                value = value.replace(group, "")
        else:
            value = value.replace(match.group(), "")
        line.write({
            self.match_field: value,
        })

    @api.multi
    def _apply_append_field(self, line, value, match):
        self.ensure_one()
        other_value = str(line[self.other_field])
        if not other_value:
            return
        end_of_match = match.end()
        value = "; ".join(part for part in [
            value[:end_of_match],
            str(line[self.other_field]),
            value[end_of_match:],
        ] if part)
        line.write({
            self.match_field: value,
        })

    @api.multi
    def _apply_merge_per_statement(self, line, value, match):
        self.ensure_one()
        match_groups = match.groupdict()
        merged_line_name = (self.other_value or _("Merged Transaction")) % {
            **match_groups,
        }
        merged_line = self.env["account.bank.statement.line"].search(
            [
                ("name", "=", merged_line_name),
                ("date", "=", line.statement_id.date),
                ("statement_id", "=", line.statement_id.id),
            ],
            limit=1,
        )
        if not merged_line:
            merged_line = self._create_new_statement_line({
                "name": merged_line_name,
                "date": line.statement_id.date,
                "statement_id": line.statement_id.id,
            })
        merged_line.amount += line.amount
        line.unlink()

    @api.multi
    def _apply_delete(self, line, value, match):
        self.ensure_one()
        line.unlink()

    @api.multi
    def _parse_decimal(self, value, currency=None):
        self.ensure_one()
        value_decimal_part = value[
            -(currency.decimal_places + 1 if currency else len(value)):
        ]
        comma_index = value_decimal_part.rfind(",")
        dot_index = value_decimal_part.rfind(".")
        if comma_index > dot_index:
            decimal_separator = ","
            thousands_separator = "."
        else:
            decimal_separator = "."
            thousands_separator = ","
        value = value.replace(thousands_separator, "")
        if decimal_separator != ".":
            value = value.replace(decimal_separator, ".")
        return Decimal(value)

    @api.multi
    def _round_decimal(self, value, currency):
        self.ensure_one()
        return value.quantize(
            Decimal(10) ** -currency.decimal_places,
            rounding=ROUND_HALF_UP
        )
