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
from openerp.tools.translate import _
from openerp.addons.account_statement_base_completion.statement import \
    ErrorTooManyPartner


class ErrorTooManyLabel(Exception):
    """New Exception definition that is raised when more than one label is
    matched by the completion rule.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AccountBankSatement(orm.Model):
    """We add a basic button and stuff to support the auto-completion
    of the bank statement once line have been imported or manually fullfill.
    """
    _inherit = "account.bank.statement"

    def open_completion_label(self, cr, uid, ids, context=None):
        return {
            'name': 'Statement Label',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.statement.label',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': False,
        }


class AccountStatementCompletionRule(orm.Model):
    _inherit = "account.statement.completion.rule"

    def get_from_label_and_partner_field(self, cr, uid, st_line, context=None):
        """Match the partner and the account based on the name field of the
        statement line and the table account.statement.label.
        If more than one statement label matched, raise the ErrorTooManylabel
        error.

        :param int line_id: id of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id': value,

            ...}
            """
        st_obj = self.pool['account.bank.statement']
        statement = st_obj.browse(cr, uid, st_line['statement_id'][0],
                                  context=context)
        res = {}
        if not context.get('label_memorizer'):
            context['label_memorizer'] = defaultdict(list)
            for line in statement.line_ids:
                cr.execute("""
                    SELECT l.partner_id,
                           l.account_id
                    FROM account_statement_label as l,
                         account_bank_statement as s
                    LEFT JOIN
                         account_bank_statement_line as st_l
                         ON
                            st_l.statement_id = s.id
                    WHERE
                        (st_l.name ~* l.label OR st_l.ref ~* l.label)
                    AND
                        l.profile_id = s.profile_id
                    AND
                        st_l.id = %s
                        """, (line.id,))
                for partner, account in cr.fetchall():
                    context['label_memorizer'][line.id].append(
                        {'partner_id': partner, 'account_id': account})
        if st_line['id'] in context['label_memorizer']:
            label_info = context['label_memorizer'][st_line['id']]
            if len(label_info) > 1:
                raise ErrorTooManyPartner(
                    _('Line named "%s" (Ref:%s) was matched by more than one '
                      'statement label.') % (st_line['name'], st_line['ref']))
            if label_info[0]['partner_id']:
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
                                      required=True,
                                      help='Account corresponding to the '
                                      'label for a given partner'),
        'company_id': fields.related('account_id', 'company_id',
                                     type='many2one',
                                     relation='res.company',
                                     string='Company',
                                     store=True,
                                     readonly=True),
        'profile_id': fields.many2one('account.statement.profile',
                                      'Account Profile'),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c:
            s.pool.get('res.company')._company_default_get(
                cr, uid, 'account.statement.label', context=c),
    }

    _sql_constraints = [
        ('profile_label_unique', 'unique (label, profile_id, company_id)',
         'You cannot have similar label for the same profile and company'),
    ]

    def save_and_close_label(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
