# -*- coding: utf-8 -*-
# © 2013-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models, fields


def _update_partner_values(wizard, values):
    """
    Updates the new partner values with the values from the wizard

    :param wizard: read record of wizard (with load='_classic_write')
    :param values: the dictionary of partner values that will be updated
    """
    copy_fields = [
        'is_company',
        'name',
        'street',
        'street2',
        'zip',
        'city',
        'country_id',
        'state_id',
        'phone',
        'fax',
        'mobile',
        'email',
    ]
    for field in copy_fields:
        if wizard[field]:
            values[field] = wizard[field]
    return values


class LinkPartner(models.TransientModel):
    """Wizard to create partner using information in bank account."""
    _name = 'banking.link_partner'
    _description = 'Link partner'

    name = fields.Char(
        string='Create partner with name',
        size=128,
        required=True,
    )
    supplier = fields.Boolean()
    customer = fields.Boolean()
    partner_id = fields.Many2one(
        string='or link existing partner',
        comodel_name='res.partner',
        domain=[
            '|', ('is_company', '=', True),
            ('parent_id', '=', False)
        ],
    )
    statement_line_id = fields.Many2one(
        string='Statement line',
        comodel_name='account.bank.statement.line',
        required=True,
        ondelete='cascade',
    )
    amount = fields.Float(
        readonly=True,
    )
    bank_account_id = fields.Many2one(
        string='Bank account',
        comodel_name='res.partner.bank',
        readonly=True,
    )
    ref = fields.Char(
        string='Reference',
        size=32,
        readonly=True,
    )
    message = fields.Char(
        string='Message',
        size=1024,
        readonly=True,
    )
    acc_number = fields.Char(
        string='Account number',
        size=24,
        readonly=True,
    )
    # Partner values
    street = fields.Char(
        size=128,
    )
    street2 = fields.Char(
        size=128,
    )
    zip = fields.Char(
        change_default=True,
        size=24,
    )
    city = fields.Char(
        string='City',
        size=128,
    )
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
    )
    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
    )
    email = fields.Char(
        size=240,
    )
    phone = fields.Char(
        size=64,
    )
    fax = fields.Char(
        size=64,
    )
    mobile = fields.Char(
        size=64,
    )
    is_company = fields.Boolean(
        string='Is a Company',
        default=True,
    )

    def create(self, vals):
        """
        Get default values from remote bank account linked to transaction.
        """
        if vals and vals.get('statement_line_id'):
            line_model = self.env['account.bank.statement.line']
            statement_line = line_model.browse(
                vals['statement_line_id'])
            # Get data from bank statement line:
            if not vals.get('name'):
                vals['name'] = statement_line.partner_name
            if 'supplier' not in vals and statement_line.amount < 0:
                vals['supplier'] = True
            if 'customer' not in vals and statement_line.amount > 0:
                vals['customer'] = True
            vals['message'] = statement_line.name
            vals['ref'] = statement_line.ref
            vals['amount'] = statement_line.amount
            # Get data from bank account:
            bank_account_obj = statement_line.bank_account_id
            if bank_account_obj:
                vals['bank_account_id'] = bank_account_obj.id
                if not vals.get('name'):
                    vals['name'] = bank_account_obj.owner_name
                vals.update({
                    'street': bank_account_obj.street or False,
                    'zip': bank_account_obj.zip or False,
                    'city': bank_account_obj.city or False,
                    'country_id':
                        bank_account_obj.country_id and
                        bank_account_obj.country_id.id or False,
                    'acc_number': bank_account_obj.acc_number or False,
                })
        return super(LinkPartner, self).create(vals)

    @api.one
    def link_partner(self):
        """Update transaction lines with partner_id and name from wizard."""
        line_model = self.env['account.bank.statement.line']
        partner_model = self.env['res.partner']

        if self.partner_id:
            partner_id = self.partner_id.id
            partner_name = self.partner_id.name
        else:
            wiz_read = self.read(load='_classic_write')[0]
            partner_vals = {
                'type': 'default',
            }
            partner_vals = _update_partner_values(wiz_read, partner_vals)
            partner_name = partner_vals['name']
            partner_obj = partner_model.create(partner_vals)
            partner_id = partner_obj.id
        # If we have a bank_account_id, update ALL statement lines with the
        # right partner (if not already set)
        statement_vals = {
            'partner_id': partner_id,
            'partner_name': partner_name,
        }
        # First update statement we came from:
        if self.statement_line_id:
            self.statement_line_id.write(statement_vals)
        # Now the other ones:
        if self.bank_account_id:
            update_ids = line_model.search(
                [
                    ('bank_account_id', '=', self.bank_account_id.id),
                    ('partner_id', '=', False),
                    ('id', '!=', self.statement_line_id.id),
                ],
            )
            for other_line in update_ids:
                other_line.write(statement_vals)
        # Ready, return to bank statement, or to wherever we came from:
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def create_act_window(self, nodestroy=True):
        """
        Return a popup window for this model
        """
        return {
            'name': self._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'domain': [],
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
            'nodestroy': nodestroy,
        }
