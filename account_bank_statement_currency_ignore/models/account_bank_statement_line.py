# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    amount_currency = fields.Monetary(
        compute="_compute_amount_currency",
        inverse="_inverse_amount_currency",
        store=True,
    )
    currency_id = fields.Many2one(
        compute="_compute_currency_id",
        inverse="_inverse_currency_id",
        store=True,
    )
    ignore_currency = fields.Boolean(
        string="Ignore Currency",
    )
    original_amount_currency = fields.Monetary(
        string="Original Amount Currency",
        currency_field="original_currency_id",
        help=(
            "The original amount expressed in an optional other currency if it "
            "is a multi-currency entry."
        ),
    )
    original_currency_id = fields.Many2one(
        string="Original Currency",
        comodel_name="res.currency",
        help="The optional other currency if it is a multi-currency entry.",
    )

    @api.multi
    @api.depends("original_amount_currency", "ignore_currency")
    def _compute_amount_currency(self):
        for line in self:
            if line.ignore_currency:
                line.amount_currency = 0.0
            else:
                line.amount_currency = line.original_amount_currency

    @api.multi
    def _inverse_amount_currency(self):
        for line in self:
            if line.ignore_currency:
                raise UserError(_(
                    'Statement line is set to ignore transaction currency, '
                    'either un-ignore it prior to editing or make changes to '
                    '"Original Amount Currency" field.'
                ))
            line.original_amount_currency = line.amount_currency

    @api.multi
    @api.depends("original_currency_id", "ignore_currency")
    def _compute_currency_id(self):
        for line in self:
            if line.ignore_currency:
                line.currency_id = None
            else:
                line.currency_id = line.original_currency_id

    @api.multi
    def _inverse_currency_id(self):
        for line in self:
            if line.ignore_currency:
                raise UserError(_(
                    'Statement line is set to ignore transaction currency, '
                    'either un-ignore it prior to editing or make changes to '
                    '"Original Currency" field.'
                ))
            line.original_currency_id = line.currency_id

    @api.multi
    def action_toggle_ignore_currency(self):
        for line in self:
            line.ignore_currency = not line.ignore_currency

    @api.multi
    def action_ignore_currency(self):
        for line in self:
            line.ignore_currency = True

    @api.multi
    def action_unignore_currency(self):
        for line in self:
            line.ignore_currency = False
