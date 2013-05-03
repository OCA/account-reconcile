from openerp.tools.translate import _
import datetime
from openerp.osv import fields
from openerp.osv.orm import Model

class AccountStatementProfil(Model):
    _inherit = "account.statement.profile"

    def _write_extra_statement_lines(
            self, cr, uid, parser, result_row_list, profile, statement_id, context):
        """Prepare the global commission line if there is one.
        """
        global_commission_amount = 0
        for row in parser.result_row_list:
            global_commission_amount += row.get('commission_amount', 0.0)
        if not global_commission_amount:
            return
        partner_id = profile.partner_id and profile.partner_id.id or False
        commission_account_id = profile.commission_account_id and profile.commission_account_id.id or False
        commission_analytic_id = profile.commission_analytic_id and profile.commission_analytic_id.id or False
        comm_values = {
            'name': 'IN ' + _('Commission line'),
            'date': datetime.datetime.now().date(),
            'amount': global_commission_amount,
            'partner_id': partner_id,
            'type': 'general',
            'statement_id': statement_id,
            'account_id': commission_account_id,
            'ref': 'commission',
            'analytic_account_id': commission_analytic_id,
            # !! We set the already_completed so auto-completion will not update those values!
            'already_completed': True,
        }
        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_line_obj.create(cr, uid, comm_values, context=context)

class AccountStatementLineWithCommission(Model):
    _inherit = "account.bank.statement.line"
    _columns = {
        'commission_amount': fields.sparse(
            type='float',
            string='Line Commission Amount',
            serialization_field='additionnal_bank_fields'),
    }
