# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import datetime
import simplejson
from coda.parser import Parser
from coda.statement import AmountSign, MovementRecordType

from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from account_statement_base_import.parser.file_parser import BankStatementImportParser


class CodaFileParser(BankStatementImportParser):

    """
    CODA parser that use a define format in coda to import
    bank statement.
    """

    def __init__(self, parse_name, parser=Parser(), *args, **kwargs):
        self._parser = parser
        self._statement = None
        super(CodaFileParser, self).__init__(parse_name, *args, **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is coda_transaction
        """
        return parser_name == 'coda_transaction'

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
        Launch the parsing through the CODA Parser
        """
        statements = self._parser.parse(self.filebuffer)
        if len(statements) > 1:
            raise except_osv(_('Not supported CODA file'),
                             _('Only one statement by CODA file is supported'))
        if len(statements) == 1:
            self._statement = statements[0]
        self.result_row_list = [m for m in self._statement.movements if m.type == MovementRecordType.NORMAL]
        return True

    def _validate(self, *args, **kwargs):
        """
        No validation needed for this parser
        """
        return True

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the responsibility
        of every parser to give this dict of vals, so each one can implement his
        own way of recording the lines.
            :param:  line: a dict of vals that represent a line of result_row_list
            :return: dict of values to give to the create method of statement line,
                     it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                }
        """
        amount = line.transaction_amount
        if line.transaction_amount_sign == AmountSign.DEBIT:
            amount = - amount
        return {'name': "\n".join(filter(None, [line.counterparty_name, line.communication])),
                'date': line.entry_date or datetime.datetime.now().date(),
                'amount': amount,
                'ref': line.ref,
                # TODO, since dictionary is directly used by the AccountStatementLine in a bulk insert
                # method that bypass the ORM, we need to write by hand, the logic behind field.sparse
                # to properly serialize our additional fields ('parner_acc_number', ....) in the right
                # container field (additionnal_bank_fields)
                'additionnal_bank_fields': simplejson.dumps({'partner_acc_number': line.counterparty_number or None,
                                                             'partner_bank_bic':  line.counterparty_bic or None})}
