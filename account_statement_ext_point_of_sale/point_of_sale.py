# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
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
from openerp.addons.point_of_sale.point_of_sale import pos_session as \
    std_pos_session
from openerp.osv import orm
from openerp.tools.translate import _

if not hasattr(std_pos_session, '_prepare_bank_statement'):
    # monkey patch to fix lp:1245375
    #
    # We replace pos_session.create with the implementation in
    # mp_create below which is essentially the same, only with a call
    # to self._prepare_bank_statement.
    #
    # The default implementation has been extracted in
    # mp_prepare_bank_statement below, and can be overridden in models
    # which _inherit pos.session
    #
    # This change has been proposed for merging to fix lp:125375
    def mp_prepare_bank_statement(self, cr, uid, pos_config, journal,
                                  context=None):
        bank_values = {
            'journal_id': journal.id,
            'user_id': uid,
            'company_id': pos_config.shop_id.company_id.id
        }
        return bank_values

    def mp_create(self, cr, uid, values, context=None):
        context = context or {}
        config_id = values.get('config_id', False) or context.get(
            'default_config_id', False)
        if not config_id:
            raise orm.except_orm(
                _('Error!'),
                _("You should assign a Point of Sale to your session."))
        # journal_id is not required on the pos_config because it does not
        # exists at the installation. If nothing is configured at the
        # installation we do the minimal configuration. Impossible to do in
        # the .xml files as the CoA is not yet installed.
        jobj = self.pool.get('pos.config')
        pos_config = jobj.browse(cr, uid, config_id, context=context)
        context.update({'company_id': pos_config.shop_id.company_id.id})
        if not pos_config.journal_id:
            jid = jobj.default_get(
                cr, uid, ['journal_id'], context=context)['journal_id']
            if jid:
                jobj.write(
                    cr, uid, [pos_config.id], {'journal_id': jid},
                    context=context)
            else:
                raise orm.except_orm(
                    _('error!'),
                    _("Unable to open the session. You have to assign a sale "
                      "journal to your point of sale."))
        # define some cash journal if no payment method exists
        if not pos_config.journal_ids:
            journal_proxy = self.pool.get('account.journal')
            cashids = journal_proxy.search(
                cr, uid, [('journal_user', '=', True),
                          ('type', '=', 'cash')], context=context)
            if not cashids:
                cashids = journal_proxy.search(
                    cr, uid, [('type', '=', 'cash')], context=context)
                if not cashids:
                    cashids = journal_proxy.search(
                        cr, uid, [('journal_user', '=', True)],
                        context=context)
            jobj.write(
                cr, uid, [pos_config.id], {'journal_ids': [(6, 0, cashids)]})
        pos_config = jobj.browse(cr, uid, config_id, context=context)
        bank_statement_ids = []
        for journal in pos_config.journal_ids:
            bank_values = self._prepare_bank_statement(
                cr, uid, pos_config, journal, context)
            statement_id = self.pool.get('account.bank.statement').create(
                cr, uid, bank_values, context=context)
            bank_statement_ids.append(statement_id)
        values.update({
            'name': pos_config.sequence_id._next(),
            'statement_ids': [(6, 0, bank_statement_ids)],
            'config_id': config_id
        })
        return super(std_pos_session, self).create(cr, uid, values,
                                                   context=context)
    std_pos_session._prepare_bank_statement = mp_prepare_bank_statement
    std_pos_session.create = mp_create


class PosSession(orm.Model):
    _inherit = 'pos.session'

    def _prepare_bank_statement(self, cr, uid, pos_config, journal,
                                context=None):
        """ Override the function _mp_create. To add the bank profile to the
        statement.
        Function That was previously added to pos.session model using monkey
        patching.
        """

        bank_values = super(PosSession, self)._prepare_bank_statement(
            cr, uid, pos_config, journal, context)
        user_obj = self.pool['res.users']
        profile_obj = self.pool['account.statement.profile']
        user = user_obj.browse(cr, uid, uid, context=context)
        defaults = self.pool['account.bank.statement'].default_get(
            cr, uid, ['profile_id', 'period_id'], context=context)
        profile_ids = profile_obj.search(
            cr, uid, [('company_id', '=', user.company_id.id),
                      ('journal_id', '=', bank_values['journal_id'])],
            context=context)
        if profile_ids:
            defaults['profile_id'] = profile_ids[0]
        bank_values.update(defaults)
        return bank_values
