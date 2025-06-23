from odoo.tests.common import TransactionCase

class TestPartialSettlement(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'amount': 500,
            'payment_type': 'inbound',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
        })
        self.payment.action_post()

    def test_wizard_creation(self):
        wizard = self.env['partial.settlement.wizard'].create({
            'partner_id': self.partner.id,
            'payment_id': self.payment.id,
        })
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.payment_id, self.payment)

    def test_reconcile_without_amount(self):
        wizard = self.env['partial.settlement.wizard'].create({
            'partner_id': self.partner.id,
            'payment_id': self.payment.id,
        })
        with self.assertRaises(Exception):
            wizard.action_reconcile()
