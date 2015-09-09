//-*- coding: utf-8 -*-
//############################################################################
//
//   This module copyright (C) 2015 Therp BV <http://therp.nl>.
//
//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU Affero General Public License as
//   published by the Free Software Foundation, either version 3 of the
//   License, or (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU Affero General Public License for more details.
//
//   You should have received a copy of the GNU Affero General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//############################################################################

openerp.account_reconcile_prepare_account = function(instance)
{
    instance.web.account.bankStatementReconciliationLine.include({
        initializeCreateForm: function()
        {
            var result = this._super.apply(this, arguments);
            this.account_id_field.set('value', this.st_line.prepared_account_id);
            this.analytic_account_id_field.set('value', this.st_line.prepared_analytic_account_id);
            return result;
        },
    });
}
