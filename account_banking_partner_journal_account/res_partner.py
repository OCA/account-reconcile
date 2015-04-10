# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV (<http://therp.nl>) / BAS Solutions
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

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'property_account_payable_bank_id': fields.property(
            type='many2one',
            relation='account.account',
            string='Default bank credit account',
            help=('Optional default journal account on bank statements for '
                  'credits from this partner. Overrides the default credit '
                  'account.'),
            domain=[('type', '!=', 'view')]),
        'property_account_receivable_bank_id': fields.property(
            type='many2one',
            relation='account.account',
            string='Default bank debit account',
            help=('Optional default journal account on bank statements for '
                  'debits from this partner. Overrides the default debit '
                  'account.'),
            domain=[('type', '!=', 'view')]),
    }

    def def_journal_account_bank_decr(
            self, cr, uid, ids, context=None):
        if not ids:
            return {}
        res = super(ResPartner, self).def_journal_account_bank_decr(
            cr, uid, ids, context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.property_account_payable_bank_id:
                res[partner.id] = partner.property_account_payable_bank_id.id
        return res

    def def_journal_account_bank_incr(
            self, cr, uid, ids, context=None):
        if not ids:
            return {}
        res = super(ResPartner, self).def_journal_account_bank_incr(
            cr, uid, ids, context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.property_account_receivable_bank_id:
                res[partner.id
                    ] = partner.property_account_receivable_bank_id.id
        return res


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    def get_statement_line_for_reconciliation(self, cr, uid, st_line,
                                              context=None):
        data = super(account_bank_statement_line,
                     self).get_statement_line_for_reconciliation(
            cr, uid, st_line, context=context)
        data['account_id'] = False
        if data and data.get('partner_id'):
            pay_bank = st_line.partner_id.property_account_payable_bank_id
            rec_bank = st_line.partner_id.property_account_receivable_bank_id
            if data['amount'] <= 0 and \
               st_line.partner_id.property_account_payable_bank_id:
                data['account_id'] = [pay_bank.id, pay_bank.name_get()[-1][-1]]

            elif data['amount'] > 0 and \
                    st_line.partner_id.property_account_receivable_bank_id:
                data['account_id'] = [rec_bank.id, rec_bank.name_get()[-1][-1]]
        return data
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
