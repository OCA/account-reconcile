# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def _get_default_rule_domain(self):
        return [('company_id', '=', self.company_id.id)]

    @api.multi
    def action_apply_default_rules(self):
        for rec in self:
            rules = rec.env['bank.statement.default.rule'].search(
                rec._get_default_rule_domain())
            rules.find_default(self.line_ids)
        return False


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _prepare_default_rule_context(self):
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'account.bank.statement.line'),
            ('name', '=', 'name')], limit=1)
        expr = r'\b%s\b' % self.name
        return {
            'default_name': self.name,
            'default_company_id': self.company_id.id,
            'default_applicable_field_id': field.id,
            'default_match_label': 'match_regex',
            'default_match_label_param': expr
        }

    @api.multi
    def action_create_default_rule(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'bank_statement_default_rule',
            'action_bank_statement_default_rule')
        context = self._prepare_default_rule_context()
        res['context'] = context
        res['view_mode'] = 'form'
        res['view_type'] = 'tree,form'
        return res
