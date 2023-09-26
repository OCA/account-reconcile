from odoo import Command, models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    def _get_write_off_move_lines_dict_oca(self, residual_balance, partner_id):
        """Standard odoo _get_write_off_move_lines_dict() method, but with patches"""
        self.ensure_one()

        if self.rule_type == "invoice_matching" and (
            not self.allow_payment_tolerance or self.payment_tolerance_param == 0
        ):
            return []

        currency = self.company_id.currency_id

        lines_vals_list = []
        for line in self.line_ids:
            balance = 0.0  # Patched here
            if line.amount_type == "percentage":
                balance = currency.round(residual_balance * (line.amount / 100.0))
            elif line.amount_type == "fixed":
                balance = currency.round(
                    line.amount * (1 if residual_balance > 0.0 else -1)
                )

            if currency.is_zero(balance):
                continue

            writeoff_line = {
                "name": line.label,
                "balance": balance,
                "debit": balance > 0 and balance or 0,
                "credit": balance < 0 and -balance or 0,
                "account_id": line.account_id.id,
                "currency_id": currency.id,
                "analytic_distribution": line.analytic_distribution,
                "reconcile_model_id": self.id,
                "journal_id": line.journal_id.id,
                "tax_ids": [],
            }
            lines_vals_list.append(writeoff_line)

            residual_balance -= balance

            if line.tax_ids:
                taxes = line.tax_ids
                detected_fiscal_position = self.env[
                    "account.fiscal.position"
                ]._get_fiscal_position(self.env["res.partner"].browse(partner_id))
                if detected_fiscal_position:
                    taxes = detected_fiscal_position.map_tax(taxes)
                writeoff_line["tax_ids"] += [Command.set(taxes.ids)]
                # Multiple taxes with force_tax_included results in wrong computation, so we
                # only allow to set the force_tax_included field if we have one tax selected
                if line.force_tax_included:
                    taxes = taxes[0].with_context(force_price_include=True)
                tax_vals_list = self._get_taxes_move_lines_dict(taxes, writeoff_line)
                lines_vals_list += tax_vals_list
                if not line.force_tax_included:
                    for tax_line in tax_vals_list:
                        residual_balance -= tax_line["balance"]

        return lines_vals_list
