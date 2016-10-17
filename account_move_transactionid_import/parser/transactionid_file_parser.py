# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime
from openerp.tools import ustr
from openerp.addons.account_move_base_import.parser.file_parser import (
    FileParser, float_or_zero
)


class TransactionIDFileParser(FileParser):
    """TransactionID parser that use a define format in csv or xls to import
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
            'transaction_id': ustr,
            'label': ustr,
            'date': datetime.datetime,
            'amount': float_or_zero,
            'commission_amount': float_or_zero,
        }
        super(TransactionIDFileParser, self).__init__(
            profile, extra_fields=conversion_dict, ftype=ftype, header=header,
            **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_transaction
        """
        return parser_name == 'generic_csvxls_transaction'

    def get_move_line_vals(self, line, *args, **kwargs):
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
        amount = line.get('amount', 0.0)
        return {
            'name': line.get('label', '/'),
            'date_maturity': line.get('date', datetime.datetime.now().date()),
            'credit': amount > 0.0 and amount or 0.0,
            'debit': amount < 0.0 and -amount or 0.0,
            'transaction_ref': line.get('transaction_id', '/'),
        }
