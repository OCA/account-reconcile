# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cleared_bank_account = fields.Boolean(string='Cleared? ',
                                          help='Check if the transaction '
                                               'has cleared from the bank')
    bank_acc_rec_statement_id = fields.Many2one('bank.acc.rec.statement',
                                                string='Bank Acc Rec '
                                                       'Statement',
                                                help="The Bank Acc Rec"
                                                     " Statement linked with "
                                                     "the journal item")
    draft_assigned_to_statement = fields.Boolean(string='Assigned to '
                                                        'Statement? ',
                                                 help='Check if the move line'
                                                      ' is assigned to '
                                                      'statement lines')
