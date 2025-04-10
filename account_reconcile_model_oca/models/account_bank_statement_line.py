# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv.expression import get_unaccent_wrapper
from odoo.tools import html2plaintext

from odoo.addons.base.models.res_bank import sanitize_account_number


class AccountBankStatementLine(models.Model):
    _inherit = ("account.bank.statement.line",)

    def _retrieve_partner(self):
        self.ensure_one()

        # Retrieve the partner from the statement line.
        if self.partner_id:
            return self.partner_id

        # Retrieve the partner from the bank account.
        if self.account_number:
            account_number_nums = sanitize_account_number(self.account_number)
            if account_number_nums:
                domain = [("sanitized_acc_number", "ilike", account_number_nums)]
                for extra_domain in ([("company_id", "=", self.company_id.id)], []):
                    bank_accounts = self.env["res.partner.bank"].search(
                        extra_domain + domain
                    )
                    if len(bank_accounts.partner_id) == 1:
                        return bank_accounts.partner_id

        # Retrieve the partner from the partner name.
        if self.partner_name:
            domain = [
                ("parent_id", "=", False),
                ("name", "ilike", self.partner_name),
            ]
            for extra_domain in ([("company_id", "=", self.company_id.id)], []):
                partner = self.env["res.partner"].search(extra_domain + domain, limit=1)
                if partner:
                    return partner

        # Retrieve the partner from the 'reconcile models'.
        rec_models = self.env["account.reconcile.model"].search(
            [
                ("rule_type", "!=", "writeoff_button"),
                ("company_id", "=", self.company_id.id),
            ]
        )
        for rec_model in rec_models:
            partner = rec_model._get_partner_from_mapping(self)
            if partner and rec_model._is_applicable_for(self, partner):
                return partner

        # Retrieve the partner from statement line text values.
        st_line_text_values = self._get_st_line_strings_for_matching()
        unaccent = get_unaccent_wrapper(self._cr)
        sub_queries = []
        params = []
        for text_value in st_line_text_values:
            if not text_value:
                continue

            # Find a partner having a name contained inside the statement line values.
            # Take care a partner could contain some special characters in its name that
            # needs to be escaped.
            sub_queries.append(
                rf"""
                {unaccent("%s")} ~* ('^' || (
                   SELECT STRING_AGG(CONCAT('(?=.*\m', chunk[1], '\M)'), '')
                   FROM regexp_matches({unaccent('partner.name')}, '\w{{3,}}', 'g')
                   AS chunk
                ))
            """
            )
            params.append(text_value)

        if sub_queries:
            self.env["res.partner"].flush_model(["company_id", "name"])
            self.env["account.move.line"].flush_model(["partner_id", "company_id"])
            self._cr.execute(
                """
                    SELECT aml.partner_id
                    FROM account_move_line aml
                    JOIN res_partner partner ON
                        aml.partner_id = partner.id
                        AND partner.name IS NOT NULL
                        AND partner.active
                        AND (("""
                + ") OR (".join(sub_queries)
                + """))
                    WHERE aml.company_id = %s
                    LIMIT 1
                """,
                params + [self.company_id.id],
            )
            row = self._cr.fetchone()
            if row:
                return self.env["res.partner"].browse(row[0])

        return self.env["res.partner"]

    def _get_st_line_strings_for_matching(self, allowed_fields=None):
        """Collect the strings that could be used on the statement line to perform some
        matching.
        :param allowed_fields: A explicit list of fields to consider.
        :return: A list of strings.
        """
        self.ensure_one()

        st_line_text_values = []
        if not allowed_fields or "payment_ref" in allowed_fields:
            if self.payment_ref:
                st_line_text_values.append(self.payment_ref)
        if not allowed_fields or "narration" in allowed_fields:
            value = html2plaintext(self.narration or "")
            if value:
                st_line_text_values.append(value)
        if not allowed_fields or "ref" in allowed_fields:
            if self.ref:
                st_line_text_values.append(self.ref)
        return st_line_text_values
