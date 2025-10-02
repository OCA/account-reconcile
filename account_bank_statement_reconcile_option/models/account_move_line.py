# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, models
from odoo.osv import expression


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """
        Override to add domain on account_id if context key
        'bank_statement_reconcile_option_statement_line_id' is set
        """
        if self.env.context.get("bank_statement_reconcile_option_statement_line_id"):
            statement_line = self.env["account.bank.statement.line"].browse(
                self.env.context.get(
                    "bank_statement_reconcile_option_statement_line_id"
                )
            )
            extra_domain = []
            if statement_line.journal_id.bank_reconcile_account_allowed_ids:
                extra_domain.append(
                    (
                        "account_id",
                        "in",
                        statement_line.journal_id.bank_reconcile_account_allowed_ids.ids,
                    )
                )
            if statement_line.journal_id.search_limit_days and statement_line.date:
                date_from = statement_line.date - timedelta(
                    days=statement_line.journal_id.search_limit_days
                )
                date_to = statement_line.date + timedelta(
                    days=statement_line.journal_id.search_limit_days
                )
                extra_domain.append(("date", ">=", date_from))
                extra_domain.append(("date", "<=", date_to))
            if extra_domain:
                domain = expression.AND([extra_domain, domain])
        return super().search_fetch(domain, field_names, offset, limit, order)
