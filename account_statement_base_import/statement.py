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

from tools.translate import _
import datetime
import netsvc
logger = netsvc.Logger()
from openerp.osv.orm import Model, fields
from openerp.osv import fields, osv
# from account_statement_base_import.parser.file_parser import FileParser
from parser import new_bank_statement_parser
import sys
import traceback

class AccountStatementProfil(Model):
    _inherit = "account.statement.profil"
    
    
    def get_import_type_selection(self, cr, uid, context=None):
        """
        Has to be inherited to add parser
        """
        return [('generic_csvxls_so', 'Generic .csv/.xls based on SO Name')]
    
    
    _columns = {
        'launch_import_completion': fields.boolean("Launch completion after import", 
                help="Tic that box to automatically launch the completion on each imported\
                file using this profile."),
        'last_import_date': fields.datetime("Last Import Date"),
        'rec_log': fields.text('log', readonly=True),
        'import_type': fields.selection(get_import_type_selection, 'Type of import', required=True, 
                help = "Choose here the method by which you want to import bank statement for this profil."),
        
    }
    
    def write_logs_after_import(self, cr, uid, ids, statement_id, num_lines, context):
        if type(ids) is int:
            ids = [ids]
        for id in ids:
            log = self.read(cr, uid, id, ['rec_log'], context=context)['rec_log']
            log_line = log and log.split("\n") or []
            import_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_line[0:0] = [import_date + ' : '
                + _("Bank Statement ID %s have been imported with %s lines ") %(statement_id, num_lines)]
            log = "\n".join(log_line)
            self.write(cr, uid, id, {'rec_log' : log, 'last_import_date':import_date}, context=context)
            logger.notifyChannel('Bank Statement Import', netsvc.LOG_INFO, 
                "Bank Statement ID %s have been imported with %s lines "%(statement_id, num_lines))
        return True
    
    def create_global_commission_line(self, cr, uid, commission_global_amount, 
            result_row_list, profile, statement_id, context):
        """Create the global commission line if there is one. The global commission is computed by
        summing the commission column of each row. Feel free to override the methode to compute
        your own commission line from the result_row_list.
            :params:    cr: The DB Cursor
            :params:    uid: int/long ID of the current user in the system
            :params:    commission_global_amount: float
            :params:    result_row_list: [{'key':value}]
            :params:    profile: browserecord of account.statement.profile
            :params:    statement_id : int/long of the current importing statement ID
            :params:    context: global context
            return:     an ID of the statement line that represent the global commission
                        for the statement.
            """
        res = False
        if commission_global_amount:
            partner_id = profile.partner_id and profile.partner_id.id or False
            commission_account_id = profile.commission_account_id and profile.commission_account_id.id or False
            commission_analytic_id = profile.commission_analytic_id and profile.commission_analytic_id.id or False
            statement_line_obj = self.pool.get('account.bank.statement.line')
            comm_values = {
                'name': 'IN '+ _('Commission line'),
                'date': datetime.datetime.now().date(),
                'amount': commission_global_amount,
                'partner_id': partner_id,
                'type': 'general',
                'statement_id': statement_id,
                'account_id': commission_account_id,
                'ref': 'commission',
                'analytic_account_id': commission_analytic_id,
                # !! We set the already_completed so auto-completion will not update those values !
                'already_completed': True,
            }
            res = statement_line_obj.create(cr, uid,
                    comm_values, 
                    context=context)
        return res
        
    def prepare_statetement_lines_vals(self, cursor, uid, parser_line, 
            account_payable, account_receivable, statement_id, context):
        """Hook to change the values of a line. Overide it to compute or change
        the account or any other values (e.g. if a line is the global commission)"""
        values = {
            'name': parser_line.get('label', parser_line.get('ref','/')),
            'date': parser_line.get('date', datetime.datetime.now().date()),
            'amount': parser_line['amount'],
            'ref': parser_line['ref'],
            'type': 'customer',
            'statement_id': statement_id,
            'label': parser_line.get('label',''),
            'commission_amount': parser_line.get('commission_amount', 0.0),
            #'account_id': journal.default_debit_account_id
        }
        values['account_id'] = statement_obj.get_account_for_counterpart(
                cursor,
                uid,
                parser_line['amount'],
                account_receivable,
                account_payable
        )
        return values
    
    def statement_import(self, cursor, uid, ids, profile_id, file_stream, ftype="csv", context=None):
        """Create a bank statement with the given profile and parser. It will fullfill the bank statement
           with the values of the file providen, but will not complete data (like finding the partner, or
           the right account). This will be done in a second step with the completion rules.
        """
        context = context or {}
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        attachment_obj = self.pool.get('ir.attachment')
        prof_obj = self.pool.get("account.statement.profil")
        if not profile_id:
            raise osv.except_osv(
                    _("No Profile !"),
                    _("You must provide a valid profile to import a bank statement !"))
        prof = prof_obj.browse(cursor,uid,profile_id,context)
        
        parser = new_bank_statement_parser(prof.import_type, ftype=ftype)
        result_row_list = parser.parse(file_stream)
        # Check all key are present in account.bank.statement.line !!
        parsed_cols = result_row_list[0].keys()
        for col in parsed_cols:
            if col not in statement_line_obj._columns:
                raise osv.except_osv(
                        _("Missing column !"),
                        _("Column %s you try to import is not present in the bank statement line !") %(col))
        
        statement_id = statement_obj.create(cursor,uid,{'profile_id':prof.id,},context)        
        account_receivable, account_payable = statement_obj.get_default_pay_receiv_accounts(cursor, uid, context)
        commission_global_amount = 0.0
        try:
            # Record every line in the bank statement and compute the global commission
            # based on the commission_amount column
            for line in result_row_list:
                commission_global_amount += line.get('commission_amount', 0.0)
                values = self.prepare_statetement_lines_vals(cursor, uid, line, account_payable, 
                    account_receivable, statement_id, context)
                # we finally create the line in system
                statement_line_obj.create(cursor, uid, values, context=context)

            # we create commission line
            self.create_global_commission_line(cursor, uid, commission_global_amount, 
                result_row_list, prof, statement_id, context)

            attachment_obj.create(
                    cursor,
                    uid,
                    {
                        'name': 'statement file',
                        'datas': file_stream,
                        'datas_fname': "%s.%s"%(datetime.datetime.now().date(),
                                                ftype),
                        'res_model': 'account.bank.statement',
                        'res_id': statement_id,
                    },
                    context=context
                )   
            # If user ask to launch completion at end of import, do it !
            if prof.launch_import_completion:
                self.button_auto_completion(cursor, uid, statement_id, context)
            
            # Write the needed log infos on profile
            self.write_logs_after_import(cursor, uid, prof.id, statement_id,
                len(result_row_list), context)
                
        except Exception, exc:
            statement_obj.unlink(cursor, uid, [statement_id])
            error_type, error_value, trbk = sys.exc_info()
            st = "Error: %s\nDescription: %s\nTraceback:" % (error_type.__name__, error_value)
            st += ''.join(traceback.format_tb(trbk, 30))
            raise osv.except_osv(
                    _("Statement import error"),
                    _("The statement cannot be created : %s") %(st))
        return statement_id
        


class AccountStatementLine(Model):
    """Add sparse field on the statement line to allow to store all the
    bank infos that are given by an office."""
    _inherit = "account.bank.statement.line"

    _columns={
        'commission_amount': fields.sparse(type='float', string='Line Commission Amount', 
            serialization_field='additionnal_bank_fields'),

    }
