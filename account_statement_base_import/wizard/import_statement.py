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

from openerp.osv import orm, fields

from openerp.tools.translate import _
import os


class CreditPartnerStatementImporter(orm.TransientModel):
    _name = "credit.statement.import"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        if (context.get('active_model', False) ==
                'account.statement.profile' and
                context.get('active_ids', False)):
            ids = context['active_ids']
            assert len(
                ids) == 1, 'You cannot use this on more than one profile !'
            res['profile_id'] = ids[0]
            other_vals = self.onchange_profile_id(
                cr, uid, [], res['profile_id'], context=context)
            res.update(other_vals.get('value', {}))
        return res

    _columns = {
        'profile_id': fields.many2one('account.statement.profile',
                                      'Import configuration parameter',
                                      required=True),
        'input_statement': fields.binary('Statement file', required=True),
        'partner_id': fields.many2one('res.partner',
                                      'Credit insitute partner'),
        'journal_id': fields.many2one('account.journal',
                                      'Financial journal to use transaction'),
        'file_name': fields.char('File Name', size=128),
        'receivable_account_id': fields.many2one(
            'account.account', 'Force Receivable/Payable Account'),
        'force_partner_on_bank': fields.boolean(
            'Force partner on bank move',
            help="Tic that box if you want to use the credit insitute partner "
            "in the counterpart of the treasury/banking move."),
        'balance_check': fields.boolean(
            'Balance check',
            help="Tic that box if you want OpenERP to control the "
            "start/end balance before confirming a bank statement. "
            "If don't ticked, no balance control will be done."),
    }

    def onchange_profile_id(self, cr, uid, ids, profile_id, context=None):
        res = {}
        if profile_id:
            c = self.pool["account.statement.profile"].browse(
                cr, uid, profile_id, context=context)
            res = {'value':
                   {'partner_id': c.partner_id and c.partner_id.id or False,
                    'journal_id': c.journal_id and c.journal_id.id or False,
                    'receivable_account_id': c.receivable_account_id.id,
                    'force_partner_on_bank': c.force_partner_on_bank,
                    'balance_check': c.balance_check,
                    }
                   }
        return res

    def _check_extension(self, filename):
        (__, ftype) = os.path.splitext(filename)
        if not ftype:
            # We do not use osv exception we do not want to have it logged
            raise Exception(_('Please use a file with an extention'))
        return ftype

    def import_statement(self, cr, uid, req_id, context=None):
        """This Function import credit card agency statement"""
        context = context or {}
        if isinstance(req_id, list):
            req_id = req_id[0]
        importer = self.browse(cr, uid, req_id, context)
        ftype = self._check_extension(importer.file_name)
        context['file_name'] = importer.file_name
        sid = self.pool.get(
            'account.statement.profile').multi_statement_import(
            cr,
            uid,
            False,
            importer.profile_id.id,
            importer.input_statement,
            ftype.replace('.', ''),
            context=context
        )
        model_obj = self.pool.get('ir.model.data')
        action_obj = self.pool.get('ir.actions.act_window')
        action_id = model_obj.get_object_reference(
            cr, uid, 'account', 'action_bank_statement_tree')[1]
        res = action_obj.read(cr, uid, action_id)
        res['domain'] = res['domain'][:-1] + ",('id', 'in', %s)]" % sid
        return res
