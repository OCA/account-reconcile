# -*- coding: utf-8 -*-
# © 2013 ACSONE SA/NV
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, fields, models
from openerp.addons.account_move_base_import.models.account_move \
    import ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.move.completion.rule"

    function_to_call = fields.Selection(
        selection_add=[
            ('get_from_bank_account',
             'From bank account number (Normal or IBAN)')
        ])

    def get_from_bank_account(self, line):
        """
        Match the partner based on the partner account number field
        Then, call the generic st_line method to complete other values.
        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
        """
        partner_acc_number = line.partner_acc_number
        if not partner_acc_number:
            return {}
        res = {}
        res_bank_obj = self.env['res.partner.bank']
        banks = res_bank_obj.search_by_acc_number(partner_acc_number)
        if len(banks) > 1:
            raise ErrorTooManyPartner(_('Line named "%s"  was matched '
                                        'by more than one partner for account '
                                        'number "%s".') %
                                      (line.name,
                                       partner_acc_number))
        if len(banks) == 1:
            partner = banks[0].partner_id
            res['partner_id'] = partner.id
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partner_acc_number = fields.Char(
        string='Account Number',
        size=64,
        help="Account number of the partner")
