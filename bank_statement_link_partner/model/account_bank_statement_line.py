# -*- coding: utf-8 -*-
"""Add button to statement line to create partner from bankaccount."""
##############################################################################
#
#    Copyright (C) 2011-2015 Therp BV <http://therp.nl>.
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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
from openerp import api, models, fields
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class AccountBankStatementLine(models.Model):
    """Add button to statement line to create partner from bankaccount."""
    _inherit = 'account.bank.statement.line'

    @api.one
    @api.depends('partner_id', 'bank_account_id')
    def _get_link_partner_ok(self):
        """
        Deliver the values of the function field that
        determines if the 'link partner' wizard is show on the
        bank statement line
        """
        self.link_partner_ok = False
        if not self.partner_id and self.bank_account_id:
            self.link_partner_ok = True

    link_partner_ok = fields.Boolean(
        string='Can link partner',
        compute='_get_link_partner_ok',
    )

    @api.multi
    def link_partner(self):
        """
        Get the appropriate partner or fire a wizard to create
        or link one
        """
        # Check if the partner is already known but not shown
        # because the screen was not refreshed yet
        if self.partner_id:
            return True
        # Reuse the bank's partner if any
        if self.bank_account_id and self.bank_account_id.partner_id:
            self.write(
                {'partner_id': self.bank_account_id.partner_id.id})
            return True
        # Should not be possible, prevented by hiding button:
        if not self.bank_account_id:
            raise except_orm(
                _("Error"),
                _("No bank account available to link partner to")
            )
        # Fire the wizard to link partner and account
        wizard_model = self.env['banking.link_partner']
        wizard_obj = wizard_model.create({'statement_line_id': self.id})
        res = wizard_obj.create_act_window()
        return res[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
