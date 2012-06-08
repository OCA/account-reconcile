# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
#    Author Nicolas Bessi
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

"""
Parser for csv or xml for file containing credit transfert data from
financial institure as VISA
"""

from tools.translate import _
import base64
import csv
import tempfile
import datetime
try:
    import xlrd
except:
    raise Exception(_('Please install python lib xlrd'))

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])

# TODO extract into a lib helper module
class FileParser(object):
    def __init__(self, filebuffer, keys_to_validate=None, decode_base_64=True, ftype='csv'):
        if ftype in ('csv', 'xls'):
            self.ftype = ftype
        else:
            raise Exception(_('Invalide file type %s. please use csv or xls') % (ftype))
        self.keys_to_validate = keys_to_validate
        self.decode_base_64 = decode_base_64
        if filebuffer:
            self.filebuffer = filebuffer
        else:
            raise Exception(_('No buffer file'))

    def parse(self):
        "launch parsing of csv or xls"
        if self.decode_base_64:
            self._decode_64b_stream()
        res = None
        if self.ftype == 'csv':
            res = self.parse_csv()
        else:
            res = self.parse_xls()
        if self.keys_to_validate:
            self._validate_column(res, self.keys_to_validate)
        return res

    def _decode_64b_stream(self):
        self.filebuffer = base64.b64decode(self.filebuffer)
        return self.filebuffer

    def _validate_column(self, array_of_dict, cols):
        parsed_cols = array_of_dict[0].keys()
        for col in cols:
            if col not in parsed_cols:
                raise Exception(_('col %s not present in file') % (col))

    def parse_csv(self, delimiter=';'):
        "return an array of dict from csv file"
        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(self.filebuffer)
        # We ensure that cursor is at beginig of file
        csv_file.seek(0)
        reader = UnicodeDictReader(
                    open(csv_file.name).readlines(),
                    delimiter=delimiter
        )
        return [x for x in reader]

    def parse_xls(self):
        "return an array of dict from csv file"
        wb_file = tempfile.NamedTemporaryFile()
        wb_file.write(self.filebuffer)
        # We ensure that cursor is at beginig of file
        wb_file.seek(0)
        wb = xlrd.open_workbook(wb_file.name)
        sheet = wb.sheet_by_index(0)
        header = sheet.row_values(0)
        res = []
        for rownum in range(1, sheet.nrows):
            res.append(dict(zip(header, sheet.row_values(rownum))))
        try:
            wb_file.close()
        except Exception, e:
            pass #file is allready closed
        return res

    def _from_csv(self, result_set, conversion_rules):
        for line in result_set:
            for rule in conversion_rules:
                if conversion_rules[rule] == datetime.datetime:
                    date_string = line[rule].split(' ')[0]
                    line[rule] = datetime.datetime.strptime(date_string,
                                                            '%Y-%m-%d')
                else:
                    line[rule] = conversion_rules[rule](line[rule])
        return result_set

    def _from_xls(self, result_set, conversion_rules):
        for line in result_set:
            for rule in conversion_rules:
                if conversion_rules[rule] == datetime.datetime:
                    t_tuple = xlrd.xldate_as_tuple(line[rule], 1)
                    line[rule] = datetime.datetime(*t_tuple)
                else:
                    line[rule] = conversion_rules[rule](line[rule])
        return result_set

    def cast_rows(self, result_set, conversion_rules):
        func =  getattr(self, '_from_%s'%(self.ftype))
        return func(result_set, conversion_rules)
