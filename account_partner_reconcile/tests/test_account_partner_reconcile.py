# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
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
        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.client',
                'tag': 'manual_reconciliation_view',
            },
            res,
            'There was an error and the manual_reconciliation_view '
            'couldn\'t be opened.'
        )
        self.assertDictContainsSubset(
            {
                'partner_ids': self.partner1.ids,
                'show_mode_selector': True,
            },
            res['context'],
            'There was an error and the manual_reconciliation_view '
            'couldn\'t be opened.'
        )
