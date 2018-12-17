# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountPartnerReconcile(TransactionCase):
    """
        Tests for Account Partner Reconcile.
    """

    def setUp(self):
        super(TestAccountPartnerReconcile, self).setUp()

        self.partner1 = self.env.ref('base.res_partner_1')

    def test_account_partner_reconcile(self):
        res = self.partner1.action_open_reconcile()

        # assertDictContainsSubset is deprecated in Python <3.2
        expect = {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
        }
        self.assertDictEqual(
            expect, {k: v for k, v in res.items() if k in expect},
            'There was an error and the manual_reconciliation_view '
            'couldn\'t be opened.')

        expect = {
            'partner_ids': self.partner1.ids,
            'show_mode_selector': True,
        }
        self.assertDictEqual(
            expect, {k: v for k, v in res['context'].items() if k in expect},
            'There was an error and the manual_reconciliation_view '
            'couldn\'t be opened.')
