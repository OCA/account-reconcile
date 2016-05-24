# -*- coding: utf-8 -*-
# © 2011 Akretion
# © 2011-2016 Camptocamp SA
# © 2013 Savoir-faire Linux
# © 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""
Wizard to import financial institute date in bank statement
"""

from openerp import _, api, fields, models
import os


class CreditPartnerStatementImporter(models.TransientModel):
    _name = "credit.statement.import"

    @api.model
    def default_get(self, fields):
        ctx = self._context
        res = {}
        if (ctx.get('active_model', False) == 'account.journal' and
                ctx.get('active_ids', False)):
            ids = ctx['active_ids']
            assert len(ids) == 1, \
                'You cannot use this on more than one journal !'
            res['journal_id'] = ids[0]
            values = self.onchange_journal_id(res['journal_id'])
            res.update(values.get('value', {}))
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
        string='Credit institute partner')
    file_name = fields.Char()
    receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Force Receivable/Payable Account')
    commission_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Commission account')

    @api.multi
    def onchange_journal_id(self, journal_id):
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            return {
                'value': {
                    'partner_id': journal.partner_id.id,
                    'receivable_account_id': journal.receivable_account_id.id,
                    'commission_account_id': journal.commission_account_id.id,
                }
            }

    @api.multi
    def _check_extension(self):
        self.ensure_one()
        (__, ftype) = os.path.splitext(self.file_name)
        if not ftype:
            # We do not use osv exception we do not want to have it logged
            raise Exception(_('Please use a file with an extension'))
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
