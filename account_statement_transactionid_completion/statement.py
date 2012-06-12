# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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

from tools.translate import _
import datetime
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields


class AccountStatementProfil(Model):
    _inherit = "account.statement.profil"
    
    
class AccountBankSatement(Model):

    _inherit = "account.bank.statement"
 
class AccountStatementLine(Model):
    _inherit = "account.bank.statement.line"

    _columns={
        # 'additionnal_bank_fields' : fields.serialized('Additionnal infos from bank', help="Used by completion and import system."),
        'transaction_id': fields.sparse(type='char', string='Transaction ID', 
            size=128,
            serialization_field='additionnal_bank_fields',
            help="Transction id from the financial institute"),
    }





