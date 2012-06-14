# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
#    Author Joel Grand-Guillaume
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools.translate import _
import base64
import csv
import tempfile
import datetime
from . import file_parser
try:
    import xlrd
except:
    raise Exception(_('Please install python lib xlrd'))

class GenericFileParser(FileParser):
    """Generic parser that use a define format in csv or xls to import
    bank statement. This is mostely an example of how to proceed to create a new 
    parser, but will also be useful as it allow to import a basic flat file."""
    
    
    
    def __init__(self, parse_name = None, ftype='csv'):
        convertion_dict = {
                            'ref': unicode,
                            'label': unicode,
                            'date': datetime.datetime,
                            'amount': float,
                            'commission_amount': float
                          }
        # Order of cols does not matter but first row of the file has to be header
        keys_to_validate = ['ref', 'label', 'date', 'amount', 'commission_amount']
        
        
        super(self,GenericFileParser).__init__(parser_for = parse_name, keys_to_validate={}, ftype='csv', convertion_dict=None ):

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == 'generic_csvxls_so'






