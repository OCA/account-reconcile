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
import base64
import csv
from datetime import datetime


def UnicodeDictReader(utf8_data, **kwargs):
    sniffer = csv.Sniffer()
    pos = utf8_data.tell()
    sample_data = utf8_data.read(2048)
    utf8_data.seek(pos)
    dialect = sniffer.sniff(sample_data, delimiters=',;\t')
    csv_reader = csv.DictReader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])


class BankStatementImportParser(object):
    """
    Generic abstract class for defining parser for different files and
    format to import in a bank statement. Inherit from it to create your
    own. If your file is a .csv or .xls format, you should consider inheirt
    from the FileParser instead.
    """

    def __init__(self, profile, *args, **kwargs):
        # The name of the parser as it will be called
        self.parser_name = profile.import_type
        # The result as a list of row. One row per line of data in the file, but
        # not the commission one !
        self.result_row_list = None
        # The file buffer on which to work on
        self.filebuffer = None
        # The profile record to access its parameters in any parser method
        self.profile = profile
        self.balance_start = None
        self.balance_end = None
        self.statement_name = None
        self.statement_date = None
        self.support_multi_statements = False

    @classmethod
    def parser_for(cls, parser_name):
        """
        Override this method for every new parser, so that new_bank_statement_parser can
        return the good class from his name.
        """
        return False

    def _decode_64b_stream(self):
        """
        Decode self.filebuffer in base 64 and override it
        """
        self.filebuffer = base64.b64decode(self.filebuffer)
        return True

    def _format(self, decode_base_64=True, **kwargs):
        """
        Decode into base 64 if asked and Format the given filebuffer by calling
        _custom_format method.
        """
        if decode_base_64:
            self._decode_64b_stream()
        self._custom_format(kwargs)
        return True

    def _custom_format(self, *args, **kwargs):
        """
        Implement a method in your parser to convert format, encoding and so on before
        starting to work on datas. Work on self.filebuffer
        """
        return NotImplementedError

    def _pre(self, *args, **kwargs):
        """
        Implement a method in your parser to make a pre-treatment on datas before parsing
        them, like concatenate stuff, and so... Work on self.filebuffer
        """
        return NotImplementedError

    def _parse(self, *args, **kwargs):
        """
        Implement a method in your parser to save the result of parsing self.filebuffer
        in self.result_row_list instance property.
        """
        return NotImplementedError

    def _validate(self, *args, **kwargs):
        """
        Implement a method in your parser  to validate the self.result_row_list instance
        property and raise an error if not valid.
        """
        return NotImplementedError

    def _post(self, *args, **kwargs):
        """
        Implement a method in your parser to make some last changes on the result of parsing
        the datas, like converting dates, computing commission, ...
        """
        return NotImplementedError

    def get_st_vals(self):
        """
        This method return a dict of vals that ca be passed to
        create method of statement.
        :return: dict of vals that represent additional infos for the statement
        """
        return {
                'name': self.statement_name or '/',
                'balance_start': self.balance_start,
                'balance_end_real': self.balance_end,
                'date': self.statement_date or datetime.now()
        }

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        Implement a method in your parser that must return a dict of vals that can be
        passed to create method of statement line in order to record it. It is the responsibility
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
        return NotImplementedError

    def parse(self, filebuffer, *args, **kwargs):
        """
        This will be the method that will be called by wizard, button and so
        to parse a filebuffer by calling successively all the private method
        that need to be define for each parser.
        Return:
             [] of rows as {'key':value}

        Note: The row_list must contain only value that are present in the account.
        bank.statement.line object !!!
        """
        if filebuffer:
            self.filebuffer = filebuffer
        else:
            raise Exception(_('No buffer file given.'))
        self._format(*args, **kwargs)
        self._pre(*args, **kwargs)
        if self.support_multi_statements:
            while self._parse(*args, **kwargs):
                self._validate(*args, **kwargs)
                self._post(*args, **kwargs)
                yield self.result_row_list
        else:
            self._parse(*args, **kwargs)
            self._validate(*args, **kwargs)
            self._post(*args, **kwargs)
            yield self.result_row_list


def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def new_bank_statement_parser(profile, *args, **kwargs):
    """Return an instance of the good parser class based on the given profile.
    
    :param profile: browse_record of import profile.
    :return: class instance for given profile import type.
    """
    for cls in itersubclasses(BankStatementImportParser):
        if cls.parser_for(profile.import_type):
            return cls(profile, *args, **kwargs)
    raise ValueError
