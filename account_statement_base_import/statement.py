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
# from account_statement_base_import.parser.file_parser import FileParser
from parser import new_bank_statement_parser

class AccountStatementProfil(Model):
    _inherit = "account.statement.profil"
    
    
    def get_type_selection(self, cr, uid, context=None):
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
        for id in ids:
            log = self.read(cr, uid, id, ['rec_log'], context=context)['rec_log']
            log_line = log and log.split("\n") or []
            import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_line[0:0] = [import_date + ' : '
                + _("Bank Statement ID %s have been imported with %s lines ") %(statement_id, num_lines)]
            log = "\n".join(log_line)
            self.write(cr, uid, id, {'rec_log' : log, 'last_import_date':import_date}, context=context)
            logger.notifyChannel('Bank Statement Import', netsvc.LOG_INFO, 
                "Bank Statement ID %s have been imported with %s lines "%(statement_id, num_lines))
        return True
    
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
        else:
        prof = prof_obj.browse(cursor,uid,profile_id,context)
        partner_id = prof.partner_id and prof.partner_id.id or False
        commission_account_id = prof.commission_account_id and prof.commission_account_id.id or False
        commission_analytic_id = prof.commission_analytic_id and prof.commission_analytic_id.id or False
        
        parser = new_bank_statement_parser(parse_name=prof.import_type, ftype=ftype)
        result_row_list = parser.parse(file_stream)
        
        # Check all key are present in account.bank.statement.line !!
        parsed_cols = self.result_row_list[0].keys()
        for col in parsed_cols:
            if col not in statement_line_obj.__columns__:
                raise osv.except_osv(
                        _("Missing column !"),
                        _("Column %s you try to import is not present in the bank statement line !") %(col))
        
        statement_id = statement_obj.create(cursor,uid,{'profile_id':prof.id,},context)        
        account_receivable, account_payable = self.get_default_pay_receiv_accounts(cursor, uid, context)
        commission_global_amount = 0.0
        try:
            # Record every line in the bank statement and compute the global commission
            # based on the commission_amount column
            for line in result_row_list:
                line_partner_id = False
                line_to_reconcile = False

                commission_global_amount += line.get('commission_amount', 0.0)
                values = {
                    'name': line.get('label', line.get('ref','/')),
                    'date': line.get('date', datetime.datetime.now().date()),
                    'amount': line['amount'],
                    'ref': line['ref'],
                    'type': 'customer',
                    'statement_id': statement_id,
                    #'account_id': journal.default_debit_account_id
                }
                values['account_id'] = self.get_account_for_counterpart(
                        cursor,
                        uid,
                        line['amount'],
                        account_receivable,
                        account_payable
                )
                # we finally create the line in system
                statement_line_obj.create(cursor, uid, values, context=context)

            # we create commission line
            if commission_global_amount:
                comm_values = {
                    'name': 'IN '+ _('Commission line'),
                    'date': datetime.datetime.now().date(),
                    'amount': commission_global_amount,
                    'partner_id': partner_id,
                    'type': 'general',
                    'statement_id': statement_id,
                    'account_id': commission_account_id,
                    'ref': 'commission',
                    'analytic_account_id': commission_analytic_id
                }
                statement_line_obj.create(cursor, uid,
                        comm_values, 
                        context=context)

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
            self.write_logs_after_import(self, cr, uid, prof.id, statement_id,
                len(result_row_list), context)
                
        except Exception, exc:
            logger.notifyChannel("Statement import",
                                 netsvc.LOG_ERROR,
                                 _("Statement can not be created %s") %(exc,))

            statement_obj.unlink(cursor, uid, [statement_id])
            raise exc
        return statement_id
        


class AccountStatementLine(Model):
    """Add sparse field on the statement line to allow to store all the
    bank infos that are given by an office."""
    _inherit = "account.bank.statement.line"

    _columns={
        'commission_amount': fields.sparse(type='float', string='Line Commission Amount', 
            serialization_field='additionnal_bank_fields'),

    }
