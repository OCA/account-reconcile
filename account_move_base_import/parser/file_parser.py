# Copyright 2011 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime
import tempfile
import logging

from odoo import _
from odoo.exceptions import UserError

from .parser import AccountMoveImportParser, UnicodeDictReader

_logger = logging.getLogger(__name__)

try:
    import xlrd
except (ImportError, IOError) as err:
    _logger.debug(err)
    xlrd = False


def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    return float(val) if val else 0.0


class FileParser(AccountMoveImportParser):
    """Generic abstract class for defining parser for .csv, .xls or .xlsx file
    format.
    """

    def __init__(
            self,
            journal,
            ftype="csv",
            extra_fields=None,
            header=None,
            dialect=None,
            move_ref=None,
            **kwargs):
        """
            :param char: parse_name: The name of the parser
            :param char: ftype: extension of the file (could be csv, xls or
              xlsx)
            :param dict: extra_fields: extra fields to put into the conversion
              dict. In the format {fieldname: fieldtype}
            :param list: header : specify header fields if the csv file has no
              header
            """
        super().__init__(journal, **kwargs)
        if ftype in ("csv", "xls", "xlsx"):
            self.ftype = ftype[0:3]
        else:
            raise UserError(
                _("Invalid file type %s. Please use csv, xls or xlsx") % ftype
            )
        self.conversion_dict = extra_fields
        self.keys_to_validate = list(self.conversion_dict.keys())
        self.fieldnames = header
        self._datemode = 0  # used only for xls documents,
        # 0 means Windows mode (1900 based dates).
        # Set in _parse_xls, from the contents of the file
        self.dialect = dialect
        self.move_ref = move_ref
        self.parsed_file = None
        self.current_line = 0

    def _custom_format(self, *args, **kwargs):
        """No other work on data are needed in this parser."""
        return True

    def _pre(self, *args, **kwargs):
        """No pre-treatment needed for this parser."""
        return True

    def _parse(self, *args, **kwargs):
        """Launch the parsing through .csv, .xls or .xlsx depending on the
        given ftype
        """
        if self.parsed_file is None:
            if self.ftype == "csv":
                self.parsed_file = self._parse_csv()
            else:
                self.parsed_file = self._parse_xls()
        if self.support_multi_moves:
            if len(self.parsed_file) <= self.current_line:
                return False
            else:
                self.result_row_list = self.parsed_file[
                    self.current_line: self.current_line + 1
                ]
                self.current_line += 1
                return True
        else:
            self.result_row_list = self.parsed_file
            return True

    def _validate(self, *args, **kwargs):
        """We check that all the key of the given file (means header) are
        present in the validation key provided. Otherwise, we raise an
        Exception. We skip the validation step if the file header is provided
        separately (in the field: fieldnames).
        """
        if self.fieldnames is None:
            parsed_cols = list(self.result_row_list[0].keys())
            for col in self.keys_to_validate:
                if col not in parsed_cols:
                    raise UserError(_("Column %s not present in file") % col)
        return True

    def _post(self, *args, **kwargs):
        """Cast row type depending on the file format .csv or .xls after
        parsing the file."""
        self.result_row_list = self._cast_rows(*args, **kwargs)
        return True

    def _parse_csv(self):
        """:return: list of dict from csv file (line/rows)"""
        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(self.filebuffer)
        csv_file.flush()
        with open(csv_file.name, "rU") as fobj:
            reader = UnicodeDictReader(
                fobj, fieldnames=self.fieldnames, dialect=self.dialect
            )
            return list(reader)

    def _parse_xls(self):
        """:return: dict of dict from xls/xlsx file (line/rows)"""
        wb_file = tempfile.NamedTemporaryFile()
        wb_file.write(self.filebuffer)
        # We ensure that cursor is at beginig of file
        wb_file.seek(0)
        with xlrd.open_workbook(wb_file.name) as wb:
            self._datemode = wb.datemode
            sheet = wb.sheet_by_index(0)
            header = sheet.row_values(0)
            res = []
            for rownum in range(1, sheet.nrows):
                res.append(dict(list(zip(header, sheet.row_values(rownum)))))
        return res

    def _from_csv(self, result_set, conversion_rules):
        """Handle the converstion from the dict and handle date format from
        an .csv file.
        """
        for line in result_set:
            for rule in conversion_rules:
                if conversion_rules[rule] == datetime.datetime:
                    try:
                        date_string = line[rule].split(" ")[0]
                        line[rule] = datetime.datetime.strptime(
                            date_string, "%Y-%m-%d"
                        )
                    except ValueError as err:
                        raise UserError(
                            _(
                                "Date format is not valid."
                                " It should be YYYY-MM-DD for column: %s"
                                " value: %s \n \n \n Please check"
                                " the line with ref: %s \n \n Detail: %s"
                            )
                            % (
                                rule,
                                line.get(rule, _("Missing")),
                                line.get("ref", line),
                                repr(err),
                            )
                        )
                else:
                    try:
                        line[rule] = conversion_rules[rule](line[rule])
                    except Exception as err:
                        raise UserError(
                            _(
                                "Value %s of column %s is not valid.\n Please "
                                "check the line with ref %s:\n \n Detail: %s"
                            )
                            % (
                                line.get(rule, _("Missing")),
                                rule,
                                line.get("ref", line),
                                repr(err),
                            )
                        )
        return result_set

    def _from_xls(self, result_set, conversion_rules):
        """Handle the converstion from the dict and handle date format from
        an .csv, .xls or .xlsx file.
        """
        for line in result_set:
            for rule in conversion_rules:
                if conversion_rules[rule] == datetime.datetime:
                    try:
                        t_tuple = xlrd.xldate_as_tuple(
                            line[rule], self._datemode
                        )
                        line[rule] = datetime.datetime(*t_tuple)
                    except Exception as err:
                        raise UserError(
                            _(
                                "Date format is not valid. "
                                "Please modify the cell formatting to date "
                                "format for column: %s value: %s\n Please"
                                " check the line with ref: %s\n \n Detail: %s"
                            )
                            % (
                                rule,
                                line.get(rule, _("Missing")),
                                line.get("ref", line),
                                repr(err),
                            )
                        )
                else:
                    try:
                        line[rule] = conversion_rules[rule](line[rule])
                    except Exception as err:
                        raise UserError(
                            _(
                                "Value %s of column %s is not valid.\n Please "
                                "check the line with ref %s:\n \n Detail: %s"
                            )
                            % (
                                line.get(rule, _("Missing")),
                                rule,
                                line.get("ref", line),
                                repr(err),
                            )
                        )
        return result_set

    def _cast_rows(self, *args, **kwargs):
        """Convert the self.result_row_list using the self.conversion_dict
        providen. We call here _from_xls or _from_csv depending on the
        self.ftype variable.
        """
        func = getattr(self, "_from_%s" % self.ftype)
        res = func(self.result_row_list, self.conversion_dict)
        return res
