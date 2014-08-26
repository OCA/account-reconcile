# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (C) 2011 Akretion & Camptocamp
#    Author : Sébastien BEAU, Joel Grand-Guillaume
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
##########################################################################

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    """Add a bank label on the partner so that we can use it to match
    this partner when we found this in a statement line.
    """
    _inherit = 'res.partner'

    _columns = {
        'bank_statement_label': fields.char(
            'Bank Statement Label', size=100,
            help="Enter the various label found on your bank statement "
                 "separated by a ; If one of this label is include in the "
                 "bank statement line, the partner will be automatically "
                 "filled (as long as you use this method/rules in your "
                 "statement profile)."),
    }
