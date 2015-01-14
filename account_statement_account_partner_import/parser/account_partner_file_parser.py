# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
#
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
import datetime
from openerp.tools import ustr
from account_statement_base_import.parser.file_parser import (
    FileParser
)


class AccountPartnerFileParser(FileParser):
    """Account/Partner parser that use a define format in csv or xls to import
    bank statement.
    """

    def __init__(self, profile, ftype='csv', extra_fields=None, header=None,
                 **kwargs):
        """Add transaction_id in header keys
            :param char: profile: Reference to the profile
            :param char: ftype: extension of the file (could be csv or xls)
            :param dict: extra_fields: extra fields to add to the conversion
              dict. In the format {fieldname: fieldtype}
            :param list: header : specify header fields if the csv file has no
              header
        """
        conversion_dict = {
            'account': ustr,
            'partner': ustr,
        }
        """
            We retrieve the pool, cursor and user ID from the browsed profile
            (not available otherwise, and we want to keep the generic parser)
        """
        self.cr = profile._cr
        self.uid = profile._uid
        self.pool = profile.pool
        super(AccountPartnerFileParser, self).__init__(
            profile, extra_fields=conversion_dict, ftype=ftype, header=header,
            **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_account_partner
        """
        return parser_name == 'generic_csvxls_account_partner'

    def get_st_line_vals(self, line, *args, **kwargs):
        """This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
              result_row_list
            :return: dict of values to give to the create method of statement
              line, it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                    'label':value,
                    'commission_amount':value,
                }
        In this generic parser, the commission is given for every line, so we
        store it for each one.
        """

        # Retrieve account & partner ID from account code & partner name
        account_obj = self.pool['account.account']
        partner_obj = self.pool['res.partner']
        account = False
        partner = False

        if line.get('account'):
            accounts = account_obj.search(self.cr, self.uid,
                                          [('code', '=', line['account'])])
            if len(accounts):
                account = accounts[0]

        if line.get('partner'):
            partners = partner_obj.search(self.cr, self.uid,
                                          [('name', '=', line['partner'])])
            if len(partners):
                partner = partners[0]

        return {
            'name': line.get('label', line.get('ref', '/')),
            'date': line.get('date', datetime.datetime.now().date()),
            'amount': line.get('amount', 0.0),
            'ref': line.get('transaction_id', '/'),
            'label': line.get('label', ''),
            'commission_amount': line.get('commission_amount', 0.0),
            'account_id': account,
            'partner_id': partner,
        }
