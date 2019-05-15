# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    attachment_number = fields.Integer('Attachments',
                                       compute='_compute_attachment_number')
    requires_attachment = fields.Boolean('Requires attachment',
                                         default=False)

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'account.bank.statement.line'),
             ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count'])
                          for data in attachment_data)
        for line in self:
            line.attachment_number = attachment.get(line.id, 0)

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'account.bank.statement.line'),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'account.bank.statement.line',
                          'default_res_id': self.id,
                          'default_name': self.name,
                          }
        return res

    @api.multi
    def unlink(self):
        self.env['ir.attachment'].search(
            [('res_model', '=', 'account.bank.statement.line'),
             ('res_id', 'in', self.ids)]).unlink()
        return super(AccountBankStatementLine, self).unlink()
