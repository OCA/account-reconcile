# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Pedro Manuel Baeza Romero
#    Copyright 2013 Servicios Tecnológicos Avanzados
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

import tempfile
import datetime

from openerp.tools.translate import _
from openerp.addons.account_statement_base_import.parser import BankStatementImportParser

try:
    import ofxparse
except:
    raise Exception(_('Please install python lib ofxparse'))

class OfxParser(BankStatementImportParser):
    """Class for defining parser for OFX file format."""

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is 'ofx_so'.
        """
        return parser_name == 'ofx_so'

    def _custom_format(self, *args, **kwargs):
        """
        No other work on data are needed in this parser.
        """
        return True

    def _pre(self, *args, **kwargs):
        """
        No pre-treatment needed for this parser.
        """
        return True

    def _parse(self, *args, **kwargs):
        """
        Launch the parsing itself.
        """
        ofx_file = tempfile.NamedTemporaryFile()
        ofx_file.seek(0)
        ofx_file.write(self.filebuffer)
        ofx_file.flush()
        ofx = ofxparse.OfxParser.parse(file(ofx_file.name))
        ofx_file.close()
        res = []
        for transaction in ofx.account.statement.transactions:
            res.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'ref': transaction.type,
                'label': transaction.payee,
            })
        self.result_row_list = res
        return True

    def _validate(self, *args, **kwargs):
        """
        Nothing to do here. ofxparse trigger possible format errors.
        """
        return True

    def _post(self, *args, **kwargs):
        """
        Nothing is needed to do after parsing.
        """
        return True

    def _post(self, *args, **kwargs):
        """
        Nothing to do.
        """
        return True

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param: line: a dict of vals that represent a line of
                result_row_list
            :return: dict of values to give to the create method of statement
                line
        """
        return {
            'name': line.get('label', line.get('ref', '/')),
            'date': line.get('date', datetime.datetime.now().date()),
            'amount': line.get('amount', 0.0),
            'ref': line.get('ref', '/'),
            'label': line.get('label', ''),
        }

