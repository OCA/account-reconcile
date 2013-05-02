# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_completion_label for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from collections import defaultdict


class ErrorTooManyLabel(Exception):
    """
    New Exception definition that is raised when more than one label is matched by
    the completion rule.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AccountBankSatement(orm.Model):
    """
    We add a basic button and stuff to support the auto-completion
    of the bank statement once line have been imported or manually fullfill.
    """
    _inherit = "account.bank.statement"

    def add_completion_label(self, cr, uid, ids, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        model_data_id = model_data_obj.search(cr, uid,
                                                 [('model', '=', 'ir.ui.view'),
                                                 ('name', '=', 'statement_label_wizard_view_form')
                                                 ], context=context)
        if model_data_id:
            res_id = model_data_obj.read(cr, uid,
                                         model_data_id,
                                         ['res_id'],
                                         context=context)[0]['res_id']
        return {
            'name': 'Statement Label',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.statement.label',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }


class AccountStatementCompletionRule(orm.Model):
    _inherit = "account.statement.completion.rule"

    def get_from_label_and_partner_field(self, cr, uid, line_id, context=None):
        """
        Match the partner and the account based on the name field of the
        statement line and the table account.statement.label.
        If more than one statement label matched, raise the ErrorTooManylabel error.

        :param int line_id: id of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
            """
        st_obj = self.pool.get('account.bank.statement.line')
        label_obj = self.pool.get('account.statement.label')
        st_line = st_obj.browse(cr, uid, line_id, context=context)
        res = {}
        # As we have to iterate on each label for each line,
        # we memorize the pair to avoid
        # to redo computation for each line.
        # Following code can be done by a single SQL query
        # but this option is not really maintanable
        if not context.get('label_memorizer'):
            context['label_memorizer'] = defaultdict(list)
            label_ids = label_obj.search(cr, uid,
                                         ['|',
                                          ('profile_id', '=', st_line.statement_id.profile_id.id),
                                          ('profile_id', '=', False)],
                                         context=context)
            for label in label_obj.browse(cr, uid, label_ids, context=context):
                line_ids = st_obj.search(cr, uid,
                                         [('statement_id', '=', st_line.statement_id.id),
                                          ('name', 'ilike', label.label),
                                          ('already_completed', '=', False)],
                                         context=context)
                import pdb;pdb.set_trace()
                for line_id in line_ids:
                    context['label_memorizer'][line_id].append({'partner_id': label.partner_id.id,
                                                                'account_id': label.account_id.id})
        if st_line['id'] in context['label_memorizer']:
            label_info = context['label_memorizer'][st_line['id']]
            if len(label_info) > 1:
                raise ErrorTooManyPartner(_('Line named "%s" (Ref:%s) was matched by '
                                            'more than one statement label.') %
                                          (st_line['name'], st_line['ref']))
            res['partner_id'] = label_info[0]['partner_id']
            res['account_id'] = label_info[0]['account_id']
        return res


class AccountStatementLabel(orm.Model):
    """Create a new class to map an account statement label to a partner
    and a specific account
    """
    _name = "account.statement.label"

    _description = "Account Statement Label"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'label': fields.char('Bank Statement Label', size=100),
        'account_id': fields.many2one('account.account', 'Account',
                                      help='Account corresponding to the label '
                                      'for a given partner'),
        'company_id': fields.many2one('res.company', 'Company'),
        'profile_id': fields.many2one('account.statement.profile',
                                      'Account Profile'),
    }

    _defaults = {
        'company_id': lambda s,cr,uid,c:
            s.pool.get('res.company')._company_default_get(cr, uid,
                                                           'account.statement.label',
                                                           context=c),
    }

    _sql_constraints = [
        ('profile_label_unique', 'unique (label, profile_id, company_id)',
         'You cannot have similar label for the same profile and company'),
    ]

    def save_and_close_label(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}