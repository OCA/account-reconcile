# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.multi
    def _compute_bank_statement_journal(self):
        obj_journal = self.env["account.journal"]
        for user in self:
            criteria = [
                "&",
                ("type", "=", "bank"),
                "|",
                ("bank_statement_allowed_group_ids", "=", False),
                "&",
                ("bank_statement_allowed_group_ids", "!=", False),
                ("id", "in", user.groups_id.mapped(
                    "allowed_bank_statement_journal_ids.id")),
            ]
            journal_ids = obj_journal.search(criteria).mapped(
                "id")

            self.bank_statement_allowed_journal_ids = journal_ids

    @api.multi
    def _compute_cash_register_journal(self):
        obj_journal = self.env["account.journal"]
        for user in self:
            criteria = [
                "&",
                ("type", "=", "cash"),
                "|",
                ("cash_register_allowed_group_ids", "=", False),
                "&",
                ("cash_register_allowed_group_ids", "!=", False),
                ("id", "in", user.groups_id.mapped(
                    "allowed_cash_register_journal_ids.id")),
            ]
            journal_ids = obj_journal.search(criteria).mapped(
                "id")

            self.cash_register_allowed_journal_ids = journal_ids

    bank_statement_allowed_journal_ids = fields.Many2many(
        string="Allowed Bank Statement Journal",
        comodel_name="account.journal",
        compute="_compute_bank_statement_journal",
    )

    cash_register_allowed_journal_ids = fields.Many2many(
        string="Allowed Cash Register Journal",
        comodel_name="account.journal",
        compute="_compute_cash_register_journal",
    )
