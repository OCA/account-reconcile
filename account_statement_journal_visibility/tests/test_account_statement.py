# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountStatement(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestAccountStatement, self).setUp(*args, **kwargs)

        self.obj_journal = self.env["account.journal"]
        self.user_admin = self.env.ref("base.user_root")
        self.group_test = self.env["res.groups"].create(
            {"name": "Test Group"})
        self.view_bs = self.env.ref("account.view_bank_statement_form")
        self.view_cr = self.env.ref("account.view_bank_statement_form2")
        self.bank_journals = self.obj_journal.search(
            [("type", "=", "bank")])
        self.bank_journal_ids = self.bank_journals.mapped("id")

        self.cash_journals = self.obj_journal.search(
            [("type", "=", "cash")])
        self.cash_journal_ids = self.cash_journals.mapped("id")

        return result

    def test_1(self):
        self.assertEqual(
            self.user_admin.bank_statement_allowed_journal_ids,
            self.bank_journals
        )

        self.bank_journals[0].write({
            "bank_statement_allowed_group_ids": [(6, 0, [self.group_test.id])],
        })

        self.assertEqual(
            len(self.bank_journals[0].bank_statement_allowed_group_ids),
            1)

    def test_2(self):
        self.assertEqual(
            self.user_admin.cash_register_allowed_journal_ids,
            self.cash_journals
        )

        self.cash_journals[0].write({
            "cash_register_allowed_group_ids": [(6, 0, [self.group_test.id])],
        })

        self.assertEqual(
            len(self.cash_journals[0].cash_register_allowed_group_ids),
            1)
