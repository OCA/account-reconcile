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
import sys
import traceback

from openerp.tools.translate import _
import datetime
from openerp.osv.orm import Model
from openerp.osv import fields, osv
from parser import new_bank_statement_parser
from openerp.tools.config import config


class AccountStatementProfil(Model):
    _inherit = "account.statement.profile"

    def get_import_type_selection(self, cr, uid, context=None):
        """This is the method to be inherited for adding the parser"""
        return [('generic_csvxls_so', 'Generic .csv/.xls based on SO Name')]

    def _get_import_type_selection(self, cr, uid, context=None):
        return self.get_import_type_selection(cr, uid, context=context)

    _columns = {
        'launch_import_completion': fields.boolean(
            "Launch completion after import",
            help="Tic that box to automatically launch the completion "
                 "on each imported file using this profile."),
        'last_import_date': fields.datetime("Last Import Date"),
        #  we remove deprecated as it floods logs in standard/warning level sob...
        'rec_log': fields.text('log', readonly=True),  # Deprecated
        'import_type': fields.selection(
            _get_import_type_selection,
            'Type of import',
            required=True,
            help="Choose here the method by which you want to import bank"
                 "statement for this profile."),
    }

    _defaults = {
                'import_type': 'generic_csvxls_so'
            }

    def _write_extra_statement_lines(
            self, cr, uid, parser, result_row_list, profile, statement_id, context):
        """Insert extra lines after the main statement lines.

        After the main statement lines have been created, you can override this method to create
        extra statement lines.

            :param:    browse_record of the current parser
            :param:    result_row_list: [{'key':value}]
            :param:    profile: browserecord of account.statement.profile
            :param:    statement_id: int/long of the current importing statement ID
            :param:    context: global context
        """
        pass

    def write_logs_after_import(self, cr, uid, ids, statement_id, num_lines, context):
        """
        Write the log in the logger

        :param int/long statement_id: ID of the concerned account.bank.statement
        :param int/long num_lines: Number of line that have been parsed
        :return: True
        """
        self.message_post(cr,
                          uid,
                          ids,
                          body=_('Statement ID %s have been imported with %s lines.') %
                                (statement_id, num_lines),
                          context=context)
        return True

    #Deprecated remove on V8
    def prepare_statetement_lines_vals(self, *args, **kwargs):
        return self.prepare_statement_lines_vals(*args, **kwargs)

    def prepare_statement_lines_vals(
            self, cr, uid, parser_vals,
            statement_id, context):
        """
        Hook to build the values of a line from the parser returned values. At
        least it fullfill the statement_id. Overide it to add your
        own completion if needed.

        :param dict of vals from parser for account.bank.statement.line (called by
                parser.get_st_line_vals)
        :param int/long statement_id: ID of the concerned account.bank.statement
        :return: dict of vals that will be passed to create method of statement line.
        """
        statement_line_obj = self.pool['account.bank.statement.line']
        values = parser_vals
        values['statement_id'] = statement_id
        date = values.get('date')
        period_memoizer = context.get('period_memoizer')
        if not period_memoizer:
            period_memoizer = {}
            context['period_memoizer'] = period_memoizer
        if period_memoizer.get(date):
            values['period_id'] = period_memoizer[date]
        else:
            # This is awfully slow...
            periods = self.pool.get('account.period').find(cr, uid,
                                                           dt=values.get('date'),
                                                           context=context)
            values['period_id'] = periods[0]
            period_memoizer[date] = periods[0]
        values = statement_line_obj._add_missing_default_values(cr, uid, values, context)
        return values

    def prepare_statement_vals(self, cr, uid, profile_id, result_row_list, parser, context):
        """
        Hook to build the values of the statement from the parser and
        the profile.
        """
        vals = {'profile_id': profile_id}
        vals.update(parser.get_st_vals())
        return vals

    def multi_statement_import(self, cr, uid, ids, profile_id, file_stream,
                               ftype="csv", context=None):
        """
        Create multiple bank statements from values given by the parser for the
         givenprofile.

        :param int/long profile_id: ID of the profile used to import the file
        :param filebuffer file_stream: binary of the providen file
        :param char: ftype represent the file exstension (csv by default)
        :return: list: list of ids of the created account.bank.statemênt
        """
        prof_obj = self.pool['account.statement.profile']
        if not profile_id:
            raise osv.except_osv(_("No Profile!"),
             _("You must provide a valid profile to import a bank statement!"))
        prof = prof_obj.browse(cr, uid, profile_id, context=context)

        parser = new_bank_statement_parser(prof, ftype=ftype)
        res = []
        for result_row_list in parser.parse(file_stream):
            statement_id = self._statement_import(cr, uid, ids, prof, parser,
                                    file_stream, ftype=ftype, context=context)
            res.append(statement_id)
        return res

    def _statement_import(self, cr, uid, ids, prof, parser, file_stream, ftype="csv", context=None):
        """
        Create a bank statement with the given profile and parser. It will fullfill the bank statement
        with the values of the file providen, but will not complete data (like finding the partner, or
        the right account). This will be done in a second step with the completion rules.

        :param prof : The profile used to import the file
        :param parser: the parser
        :param filebuffer file_stream: binary of the providen file
        :param char: ftype represent the file exstension (csv by default)
        :return: ID of the created account.bank.statemênt
        """
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        attachment_obj = self.pool.get('ir.attachment')

        result_row_list = parser.result_row_list
        # Check all key are present in account.bank.statement.line!!
        if not result_row_list:
            raise osv.except_osv(_("Nothing to import"),
                                 _("The file is empty"))
        parsed_cols = parser.get_st_line_vals(result_row_list[0]).keys()
        for col in parsed_cols:
            if col not in statement_line_obj._columns:
                raise osv.except_osv(_("Missing column!"),
                                     _("Column %s you try to import is not "
                                       "present in the bank statement line!") % col)

        statement_vals = self.prepare_statement_vals(cr, uid, prof.id, result_row_list, parser, context)
        statement_id = statement_obj.create(cr, uid,
                                            statement_vals,
                                            context=context)

        try:
            # Record every line in the bank statement
            statement_store = []
            for line in result_row_list:
                parser_vals = parser.get_st_line_vals(line)
                values = self.prepare_statement_lines_vals(
                    cr, uid, parser_vals, statement_id,
                    context)
                statement_store.append(values)
            # Hack to bypass ORM poor perfomance. Sob...
            statement_line_obj._insert_lines(cr, uid, statement_store, context=context)

            self._write_extra_statement_lines(
                cr, uid, parser, result_row_list, prof, statement_id, context)
            # Trigger store field computation if someone has better idea
            start_bal = statement_obj.read(
                cr, uid, statement_id, ['balance_start'], context=context)
            start_bal = start_bal['balance_start']
            statement_obj.write(cr, uid, [statement_id], {'balance_start': start_bal})

            attachment_data = {
                'name': 'statement file',
                'datas': file_stream,
                'datas_fname': "%s.%s" % (datetime.datetime.now().date(), ftype),
                'res_model': 'account.bank.statement',
                'res_id': statement_id,
            }
            attachment_obj.create(cr, uid, attachment_data, context=context)

            # If user ask to launch completion at end of import, do it!
            if prof.launch_import_completion:
                statement_obj.button_auto_completion(cr, uid, [statement_id], context)

            # Write the needed log infos on profile
            self.write_logs_after_import(cr, uid, prof.id,
                                         statement_id,
                                         len(result_row_list),
                                         context)

        except Exception:
            error_type, error_value, trbk = sys.exc_info()
            st = "Error: %s\nDescription: %s\nTraceback:" % (error_type.__name__, error_value)
            st += ''.join(traceback.format_tb(trbk, 30))
            #TODO we should catch correctly the exception with a python
            #Exception and only re-catch some special exception.
            #For now we avoid re-catching error in debug mode
            if config['debug_mode']:
                raise
            raise osv.except_osv(_("Statement import error"),
                                 _("The statement cannot be created: %s") % st)
        return statement_id
