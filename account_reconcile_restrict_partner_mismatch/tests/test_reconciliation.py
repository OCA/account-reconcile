# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.exceptions import UserError


class TestReconciliation(AccountingTestCase):

    def setUp(self):
        super(TestReconciliation, self).setUp()
        self.env = self.env(context=dict(
            self.env.context, tracking_disable=True,
            test_partner_mismatch=True)
        )

        self.partner = self.env.ref("base.res_partner_2")
        self.partner_id = self.partner.id
        rec_type = self.env['account.account'].search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_receivable').id)
        ], limit=1)
        pay_type = self.env['account.account'].search([
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_payable').id)
        ], limit=1)
        self.account_rcv = (self.partner.property_account_receivable_id
                            or rec_type)
        self.account_rsa = self.partner.property_account_payable_id or pay_type

        self.bank_journal = self.env['account.journal']. \
            create({'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        self.aml = self.init_moves()
        self.wizard = self.env['account.move.line.reconcile.writeoff']. \
            with_context(active_ids=[x.id for x in self.aml]).create({
                'journal_id': self.bank_journal.id,
                'writeoff_acc_id': self.account_rsa.id
            })

    def create_move(self, name, amount):
        debit_line_vals = {
            'name': name,
            'debit': amount > 0 and amount or 0.0,
            'credit': amount < 0 and -amount or 0.0,
            'account_id': self.account_rcv.id,
        }
        credit_line_vals = debit_line_vals.copy()
        credit_line_vals['debit'] = debit_line_vals['credit']
        credit_line_vals['credit'] = debit_line_vals['debit']
        credit_line_vals['account_id'] = self.account_rsa.id
        vals = {
            'journal_id': self.bank_journal.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        }
        return self.env['account.move'].create(vals).id

    def init_moves(self):
        move_list_vals = [
            ('1', -1.83),
            ('2', 728.35),
            ('3', -4.46),
            ('4', 0.32),
            ('5', 14.72),
            ('6', -737.10),
        ]
        move_ids = []
        for name, amount in move_list_vals:
            move_ids.append(self.create_move(name, amount))
        aml_recs = self.env['account.move.line'].search([
            ('move_id', 'in', move_ids),
            ('account_id', '=', self.account_rcv.id)
        ])
        return aml_recs

    def test_reconcile_no_partner(self):
        self.wizard.trans_rec_reconcile()
        self.assertTrue(all(self.aml.mapped('reconciled')))

    def test_reconcile_partner_mismatch(self):
        self.aml[0].partner_id = self.partner.id
        with self.assertRaises(UserError):
            self.wizard.trans_rec_reconcile()
        # all lines with same partner allowed
        self.aml.write({'partner_id': self.partner.id})
        self.wizard.trans_rec_reconcile()
        self.assertTrue(all(self.aml.mapped('reconciled')))

    def test_reconcile_accounts_excluded(self):
        self.aml[0].partner_id = self.partner.id
        with self.assertRaises(UserError):
            self.wizard.trans_rec_reconcile()
        # reconciliation forbiden only for certain types of accounts
        account = self.env['account.account'].search([
            ('user_type_id.type', '=', 'other')
        ], limit=1)
        account.reconcile = True
        self.aml[0].account_id = account.id
        with self.assertRaises(UserError):
            self.wizard.trans_rec_reconcile()
        # reconciliation for different partners allowed
        # for not forbidden types
        self.aml.write({'account_id': account.id})
        self.wizard.trans_rec_reconcile()
        self.assertTrue(all(self.aml.mapped('reconciled')))
