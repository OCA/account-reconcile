# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResGroups(models.Model):
    _inherit = "res.groups"

    allowed_bank_statement_journal_ids = fields.Many2many(
        string="Allowed Bank Statement Journals",
        comodel_name="account.journal",
        relation="rel_allowed_bank_statement_journal_for_group",
        column1="group_id",
        column2="journal_id",
    )

    allowed_cash_register_journal_ids = fields.Many2many(
        string="Allowed Cash Register Journals",
        comodel_name="account.journal",
        relation="rel_allowed_cash_register_journal_for_group",
        column1="group_id",
        column2="journal_id",
    )
