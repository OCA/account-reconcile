from odoo import _, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    # TODO: Delete if merged https://github.com/odoo/odoo/pull/182497
    def _compute_date_index(self):
        """The super() method does not take into account lines that do not have
        internal_index set yet, and causes sorted() to fail, we need to re-define
        the method in these cases to avoid the error.
        """
        _self = self
        for stmt in self:
            if any(not line.internal_index for line in stmt.line_ids):
                _self -= stmt
                sorted_lines = stmt.line_ids.filtered("internal_index").sorted(
                    "internal_index"
                )
                stmt.first_line_index = sorted_lines[:1].internal_index
                stmt.date = sorted_lines.filtered(lambda l: l.state == "posted")[
                    -1:
                ].date
        return super(AccountBankStatement, _self)._compute_date_index()

    def action_open_statement_lines(self):
        self.ensure_one()
        if not self:
            return {}
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_statement_base.account_bank_statement_line_action"
        )
        action.update(
            {
                "domain": [("statement_id", "=", self.id)],
                "context": {
                    "default_journal_id": self._context.get("active_id")
                    if self._context.get("active_model") == "account.journal"
                    else None,
                    "account_bank_statement_line_main_view": True,
                },
            }
        )

        return action

    def open_entries(self):
        self.ensure_one()
        return {
            "name": _("Journal Items"),
            "view_mode": "tree,form",
            "res_model": "account.move.line",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": {"search_default_group_by_move": 1, "expand": 1},
            "search_view_id": self.env.ref("account.view_account_move_line_filter").id,
            "domain": [
                "&",
                ("parent_state", "=", "posted"),
                ("statement_id", "=", self.id),
            ],
        }
