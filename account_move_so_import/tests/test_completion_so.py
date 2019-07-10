# Copyright 2011-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestCompliteSO(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env.ref('base.res_partner_1')
        p = cls.env.ref('product.product_product_6')
        cls.order = cls.env['sale.order'].create({
            'name': 'Test order',
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'name': 'Test autocomplet',
                                   'product_id': p.id,
                                   'product_uom_qty': 2,
                                   'qty_to_invoice': 2,
                                   'qty_delivered': 2,
                                   'product_uom': p.uom_id.id,
                                   'price_unit': p.list_price})],
        })
        rule_ids = cls.env.ref('account_move_base_import.'
                               'bank_statement_completion_rule_5')
        rule_ids += cls.env.ref('account_move_base_import.'
                                'bank_statement_completion_rule_4')
        rule_ids += cls.env.ref('account_move_base_import.'
                                'bank_statement_completion_rule_3')
        rule_ids += cls.env.ref('account_move_base_import.'
                                'bank_statement_completion_rule_2')
        rule_ids += cls.env.ref('account_move_so_import.'
                                'bank_statement_completion_rule_1')
        # create journal with profile
        cls.journal = cls.env['account.journal'].create({
            'name': 'Company Bank journal',
            'type': 'bank',
            'code': 'BNKFB',
            'rule_ids': [
                (4, comp_rule.id, False) for comp_rule in rule_ids
            ],
            'used_for_completion': True,
        })
        cls.move = cls.env['account.move'].create(
            {'name': 'Test move', 'journal_id': cls.journal.id}
        )
        cls.account_payable = cls.env['account.account'].search([
            ('user_type_id', '=',
             cls.env.ref('account.data_account_type_payable').id),
        ], limit=1)

    def test_completion_so(self):
        self.order.action_confirm()
        aml = self.env['account.move.line'].create(
            {
                'name': self.order.name,
                'account_id': self.account_payable.id,
                'move_id': self.move.id,
                'credit': 0.0,
            }
        )
        aml.with_context(check_move_validity=False).write({
            'credit': 1,
        })
        self.assertFalse(self.move.partner_id)
        self.move.button_auto_completion()
        self.assertEqual(self.move.partner_id, self.partner,)
