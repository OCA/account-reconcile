# -*- coding: utf-8 -*-
# © 2011-2016 Akretion
# © 2011-2016 Camptocamp SA
# © 2013 Savoir-faire Linux
# © 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""
Wizard to import financial institute date in bank statement
"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import os


class CreditPartnerStatementImporter(models.TransientModel):
    _name = "credit.statement.import"
    _description = 'Import Batch File wizard'

    @api.model
    def default_get(self, fields):
        ctx = self._context
        res = {}
        if (
                ctx.get('active_model') == 'account.journal' and
                ctx.get('active_ids')):
            ids = ctx['active_ids']
            assert len(ids) == 1, \
                'You cannot use this on more than one journal !'
            res['journal_id'] = ids[0]
        return res

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Import configuration parameter',
        required=True)
    input_statement = fields.Binary(
        string='Statement file',
        required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='journal_id.partner_id', readonly=True)
    file_name = fields.Char()
    receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        related='journal_id.receivable_account_id', readonly=True)
    commission_account_id = fields.Many2one(
        comodel_name='account.account',
        related='journal_id.commission_account_id', readonly=True)

    @api.multi
    def _check_extension(self):
        self.ensure_one()
        (__, ftype) = os.path.splitext(self.file_name)
        if not ftype:
            raise UserError(_('Please use a file with an extension'))
        return ftype

    @api.multi
    def import_statement(self):
        """This Function import credit card agency statement"""
        moves = self.env['account.move']
        for importer in self:
            journal = importer.journal_id
            ftype = importer._check_extension()
            moves |= journal.with_context(
                file_name=importer.file_name).multi_move_import(
                importer.input_statement,
                ftype.replace('.', '')
            )
        xmlid = ('account', 'action_move_journal_line')
        action = self.env['ir.actions.act_window'].for_xml_id(*xmlid)
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        else:
            ref = self.env.ref('account.view_move_form')
            action['views'] = [(ref.id, 'form')]
            action['res_id'] = moves.id if moves else False
        return action
