# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_data_locked = fields.Boolean(
        string="Datos Fiscales Bloqueados",
        default=lambda self: self._default_fiscal_data_locked(),
    )
    partner_fiscal_data = fields.Html(
        string="Cliente", compute="_compute_partner_fiscal_data", store=1
    )

    @api.depends("partner_id", "fiscal_data_locked")
    def _compute_partner_fiscal_data(self):
        def complete_partner_fiscal_data(rec):
            data = ""
            if rec.partner_id.name:
                data = rec.partner_id.name
            if rec.partner_id.street:
                data += "<br/>" + rec.partner_id.street + "<br/>"
            if rec.partner_id.zip:
                data += rec.partner_id.zip
            if rec.partner_id.city:
                data += " " + rec.partner_id.city
            if rec.partner_id.country_id:
                data += "<br/>" + rec.partner_id.country_id.name
            if rec.partner_id.vat:
                data += " - " + rec.partner_id.vat
            return data

        for rec in self:
            # First time
            if not rec.partner_fiscal_data and rec.partner_id:
                rec.partner_fiscal_data = complete_partner_fiscal_data(rec)
                continue
            if not rec.fiscal_data_locked and rec.partner_id:
                rec.partner_fiscal_data = complete_partner_fiscal_data(rec)

    def _default_fiscal_data_locked(self):
        if self._context.get("default_state") in ["draft", "button_draft"]:
            return False
        elif self._context.get("default_state") == "posted":
            return True

    @api.model
    def write(self, vals):
        if "state" in vals:
            new_state = vals["state"]
            if new_state == "posted":
                vals["fiscal_data_locked"] = True
                vals["partner_fiscal_data"] = self._compute_partner_fiscal_data()
            elif new_state in ["draft", "cancel"]:
                vals["fiscal_data_locked"] = False
        return super(AccountMove, self).write(vals)
