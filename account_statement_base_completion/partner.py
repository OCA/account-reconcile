# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import fields, osv

class res_partner(osv.osv):
    """Add a bank label on the partner so that we can use it to match
    this partner when we found this in a statement line."""
    _inherit = 'res.partner'

    _columns = {
        'bank_statement_label':fields.char('Bank Statement Label', size=100,
                help="Enter the various label found on your bank statement separated by a ; If \
                 one of this label is include in the bank statement line, the partner will be automatically \
                 filled (as long as you use thi method in your statement profile)."),
            }

    # def get_partner_from_order_ref(self, cr, uid, order_ref, context=None):
    #     order_obj = self.pool.get('sale.order')
    #     so_id = order_obj.search(cr, uid, [('name', '=', order_ref)], context=context)
    #     if so_id:
    #         so = order_obj.browse(cr, uid, so_id, context=context)[0]
    #         return so.partner_id.id
    #     return False
    #     
    # def get_partner_from_name(self, cr, uid, partner_name, context=None):
    #     #print 'try to get partner from name', partner_name
    #     return False
    #     
    # def get_partner_from_email(self, cr, uid, partner_email, context=None):
    #     address_ids = self.pool.get('res.partner.address').search(cr, uid, [['email', '=', partner_email]], context=context)
    #     if address_ids:
    #         partner_id = self.search(cr, uid, [['address', 'in', address_ids]], context=context)
    #         return partner_id and partner_id[0]
    #     return False

    def get_partner_from_label_based_on_bank_statement_label(self, cr, uid, label, context=None):
        ids = self.search(cr, uid, [['bank_statement_label', '!=', False]], context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            for partner_label in partner.bank_statement_label.split(';'):
                if partner_label in label:
                    return partner.id
        return False

    def get_supplier_partner_from_label_based_on_name(self, cr, uid, label, context=None):
        supplier_ids = self.search(cr, uid, [['supplier', '=', True]], context=context)
        for partner in self.browse(cr, uid, supplier_ids, context=context):
            if partner.name in label:
                return partner.id
        return False

    def get_partner_account(self, cr, uid, id, amount, context=None):
        partner = self.browse(cr, uid, id, context=context)
        if partner.supplier and not partner.customer:
            return partner.property_account_payable.id
        if partner.customer and not partner.supplier:
            return partner.property_account_receivable.id
        
        if amount >0:
            return partner.property_account_receivable.id
        else:
            return partner.property_account_payable.id



res_partner()
