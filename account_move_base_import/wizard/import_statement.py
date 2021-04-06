# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""
Wizard to import financial institute date in bank statement
"""

import os

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreditPartnerStatementImporter(models.TransientModel):
    _name = "credit.statement.import"
    _description = "Import Batch File wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        ctx = self.env.context
        if ctx.get("active_model") == "account.journal" and ctx.get("active_ids"):
            ids = ctx["active_ids"]
            assert len(ids) == 1, "You cannot use this on more than one journal !"
            res["journal_id"] = ids[0]
        return res

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Import configuration parameter",
        required=True,
    )
    input_statement = fields.Binary(string="Statement file", required=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="journal_id.partner_id", readonly=True
    )
    file_name = fields.Char()
    receivable_account_id = fields.Many2one(
        comodel_name="account.account",
        related="journal_id.receivable_account_id",
        readonly=True,
    )
    commission_account_id = fields.Many2one(
        comodel_name="account.account",
        related="journal_id.commission_account_id",
        readonly=True,
    )

    def _check_extension(self):
        self.ensure_one()
        (__, ftype) = os.path.splitext(self.file_name)
        if not ftype:
            raise UserError(_("Please use a file with an extension"))
        return ftype

    def import_statement(self):
        """This Function import credit card agency statement"""
        moves = self.env["account.move"]
        for importer in self:
            journal = importer.journal_id
            ftype = importer._check_extension()
            moves |= journal.with_context(
                file_name=importer.file_name
            ).multi_move_import(importer.input_statement, ftype.replace(".", ""))
        action = action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_journal_line"
        )
        if len(moves) > 1:
            action["domain"] = [("id", "in", moves.ids)]
        else:
            ref = self.env.ref("account.view_move_form")
            action["views"] = [(ref.id, "form")]
            action["res_id"] = moves.id if moves else False
        return action
