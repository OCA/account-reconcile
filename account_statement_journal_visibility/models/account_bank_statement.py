# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import ustr


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    journal_id = fields.Many2one(
        default=False,
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False,
                        submenu=False):
        res = super(AccountBankStatement, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != "form":
            return res

        view_bs = self.env.ref("account.view_bank_statement_form")
        view_cr = self.env.ref("account.view_bank_statement_form2")
        if view_id not in [view_bs.id, view_cr.id]:
            return res

        if view_id == view_bs.id:
            journal_ids = self.env.user.mapped(
                "bank_statement_allowed_journal_ids.id")
            domain_extra = "('id', 'in', %s)" % (str(journal_ids))
        elif view_id == view_cr.id:
            journal_ids = self.env.user.mapped(
                "cash_register_allowed_journal_ids.id")
            domain_extra = "('id', 'in', %s)" % (str(journal_ids))

        if "journal_id" not in res["fields"]:
            return res

        journal_field = res["fields"]["journal_id"]
        domain = ustr(journal_field.get("domain", "[]"))
        journal_field["domain"] = domain[:1] + domain_extra + domain[1:]

        return res
