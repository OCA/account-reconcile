from odoo import fields, models


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    accounting_date = fields.Date(
        string="Accounting Date",
        help="If set, the accounting entries created during the bank statement "
        "reconciliation process will be created at this date.\n"
        "This is useful if the accounting period in which the entries should "
        "normally be booked is already closed.",
        states={"open": [("readonly", False)]},
        readonly=True,
    )

    def action_bank_reconcile_bank_statements(self):
        self.ensure_one()
        bank_stmt_lines = self.mapped("line_ids")
        return {
            "type": "ir.actions.client",
            "tag": "bank_statement_reconciliation_view",
            "context": {
                "statement_line_ids": bank_stmt_lines.ids,
                "company_ids": self.mapped("company_id").ids,
            },
        }
