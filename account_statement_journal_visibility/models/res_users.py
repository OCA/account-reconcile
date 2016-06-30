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
            # Search journal with no additional policy
            criteria = [
                ("bank_statement_allowed_group_ids", "=", False),
                ("type", "=", "bank"),
            ]
            journal_ids = obj_journal.search(criteria).mapped(
                "id")

            # add journal with additional policy that
            # user has access to it
            self.bank_statement_allowed_journal_ids = \
                journal_ids + user.groups_id.mapped(
                    "allowed_bank_statement_journal_ids.id")

    @api.multi
    def _compute_cash_register_journal(self):
        obj_journal = self.env["account.journal"]
        for user in self:
            # Search journal with no additional policy
            criteria = [
                ("cash_register_allowed_group_ids", "=", False),
                ("type", "=", "cash"),
            ]
            journal_ids = obj_journal.search(criteria).mapped(
                "id")

            # add journal with additional policy that
            # user has access to it
            self.cash_register_allowed_journal_ids = \
                journal_ids + user.groups_id.mapped(
                    "allowed_cash_register_journal_ids.id")

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
