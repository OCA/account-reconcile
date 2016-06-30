# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    bank_statement_allowed_group_ids = fields.Many2many(
        string="Allowed Groups for Bank Statement",
        comodel_name="res.groups",
        relation="rel_allowed_bank_statement_journal_for_group",
        column1="journal_id",
        column2="group_id",
    )

    cash_register_allowed_group_ids = fields.Many2many(
        string="Allowed Groups for Cash Register",
        comodel_name="res.groups",
        relation="rel_allowed_cash_register_journal_for_group",
        column1="journal_id",
        column2="group_id",
    )
