# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time

from odoo import api, fields, models


class CreditStatementImport(models.TransientModel):
    _inherit = "credit.statement.import"

    input_statement = fields.Binary(required=False)
    need_file = fields.Boolean(compute="_compute_need_file")
    last_import_date = fields.Datetime(
        string="Import From", related="journal_id.last_import_date"
    )
    first_import_date = fields.Date(
        string="First Import From",
        help="Arrival date of the first Stripe payout to import. Leave empty to "
        "import all the payouts. Used only by the first import of the journal.",
    )

    @api.depends("journal_id")
    def _compute_need_file(self):
        for record in self:
            record.need_file = record.journal_id.import_type != "stripe"

    def _check_extension(self):
        if self.need_file:
            return super()._check_extension()
        return ""

    def import_statement(self):
        for record in self:
            if record.first_import_date and not record.journal_id.last_import_date:
                record.journal_id.last_import_date = datetime.combine(
                    record.first_import_date, time.min
                )
        return super().import_statement()
