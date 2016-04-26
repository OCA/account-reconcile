# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
Wizard to import financial institute date in bank statement
"""

from openerp import _, api, fields, models
import os


class CreditPartnerStatementImporter(models.TransientModel):
    _name = "credit.statement.import"

    @api.model
    def default_get(self, fields):
        context = self.env.context.copy()
        res = {}
        if (context.get('active_model', False) == 'account.journal' and
                context.get('active_ids', False)):
            ids = context['active_ids']
            assert len(ids) == 1, \
                'You cannot use this on more than one profile !'
            res['journal_id'] = ids[0]
            self.onchange_journal_id(res['journal_id'])
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
        string='Credit insitute partner')
    file_name = fields.Char('File Name', size=128)
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
        for importer in self:
            importer.partner_id = journal.partner_id.id
            importer.receivable_account_id = journal.receivable_account_id.id
            importer.commission_account_id = journal.commission_account_id.id

    def _check_extension(self, filename):
        (__, ftype) = os.path.splitext(filename)
        if not ftype:
            # We do not use osv exception we do not want to have it logged
            raise Exception(_('Please use a file with an extension'))
        return ftype

    @api.multi
    def import_statement(self):
        """This Function import credit card agency statement"""
        for importer in self:
            journal = importer.journal_id
            ftype = self._check_extension(importer.file_name)
            journal.with_context(
                file_name=importer.file_name).multi_move_import(
                importer.input_statement,
                ftype.replace('.', '')
            )
