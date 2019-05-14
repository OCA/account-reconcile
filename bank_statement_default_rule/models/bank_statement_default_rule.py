# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re
from odoo import api, fields, models, _


class BankStatementDefaultRule(models.Model):
    _name = 'bank.statement.default.rule'
    _description = 'Bank Statement Default Rule'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    applicable_field_id = fields.Many2one(
        'ir.model.fields', string='Applicable Field',
        required=True,
        domain="[('model_id', '=', 'account.bank.statement.line'), "
               "('ttype', 'in', ['char', 'text'])]",
    )
    match_label = fields.Selection(selection=[
        ('match_regex', 'Match Regex'),
    ], string='Label', default='match_regex', required=True)
    match_label_param = fields.Char(string='Label Parameter')
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
    )

    @api.model
    def find_default_match_regex(self, lines):
        matched_lines = lines.filtered(lambda l: re.match(
            self.match_label_param, l[self.applicable_field_id.name]))
        return matched_lines

    @api.model
    def default_values_to_update(self):
        return {'partner_id': self.partner_id.id}

    @api.multi
    def find_default(self, lines):
        for rec in self:
            if rec.match_label == 'match_regex':
                matched_lines = rec.find_default_match_regex(lines)
                vals = rec.default_values_to_update()
                for matched_line in matched_lines:
                    for val_k in vals.keys():
                        if not matched_line[val_k]:
                            matched_line.write({val_k: vals[val_k]})
        return True
