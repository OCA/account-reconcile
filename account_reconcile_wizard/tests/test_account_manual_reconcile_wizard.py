# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountManualReconcileWizard(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.expense_account = cls.company_data["default_account_expense"]
        cls.expense_account2 = cls.expense_account.copy()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.invoice1 = cls._create_invoice_one_line(
            price_unit=100.0,
            move_type="out_invoice",
            partner_id=cls.partner.id,
            post=True,
        )
        cls.invoice2 = cls._create_invoice_one_line(
            price_unit=50.0,
            move_type="out_invoice",
            partner_id=cls.partner.id,
            post=True,
        )
        cls.bill1 = cls._create_invoice_one_line(
            price_unit=100.0,
            move_type="in_invoice",
            partner_id=cls.partner.id,
            post=True,
        )
        cls.bill2 = cls._create_invoice_one_line(
            price_unit=150.0,
            move_type="in_invoice",
            partner_id=cls.partner.id,
            post=True,
        )
        cls.payment1 = cls.init_payment(100, post=True, partner=cls.partner)
        cls.reconcile_model_percentage = cls.env["account.reconcile.model"].create(
            {
                "name": "Test Reconcile Model",
                "rule_type": "writeoff_button",
                "counterpart_type": "general",
                "line_ids": [
                    Command.create(
                        {
                            "account_id": cls.expense_account.id,
                            "amount_type": "percentage",
                            "amount_string": 60.0,
                        }
                    ),
                    Command.create(
                        {
                            "account_id": cls.expense_account2.id,
                            "amount_type": "percentage",
                            "amount_string": 40.0,
                        }
                    ),
                ],
            }
        )

    def _create_reconcile_wizard(self, lines):
        return (
            self.env["account.manual.reconcile.wizard"]
            .with_context(active_model="account.move.line", active_ids=lines.ids)
            .create({})
        )

    def test_reconcile_full(self):
        """
        Invoice 1 = 100, Payment 1 = 100.
        The difference is 0, so no transfer nor write-off is needed.
        Both documents should be fully reconciled.
        """
        lines_to_reconcile = (
            self.invoice1.line_ids + self.payment1.move_id.line_ids
        ).filtered(lambda line: line.account_id.account_type == "asset_receivable")
        self.assertEqual(len(lines_to_reconcile), 2)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertFalse(wizard.need_transfer)
        self.assertFalse(wizard.need_write_off)
        self.assertTrue(wizard.allow_partial_reconcile)
        self.assertTrue(wizard.display_allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 0.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(result_lines, lines_to_reconcile)
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)

    def test_reconcile_full_with_transfer(self):
        """
        Invoice 1 = 100, Bill 1 = 100.
        The difference is 0, but with transfer,
        100 is transferred from payable to receivable, so no write-off is needed.
        Both documents should be fully reconciled.
        """
        lines_to_reconcile = (self.invoice1.line_ids + self.bill1.line_ids).filtered(
            lambda line: line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        )
        self.assertEqual(len(lines_to_reconcile), 2)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertTrue(wizard.need_transfer)
        self.assertFalse(wizard.need_write_off)
        self.assertTrue(wizard.allow_partial_reconcile)
        self.assertTrue(wizard.display_allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 0.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 4)
        new_move_lines = result_lines - lines_to_reconcile
        # Check the transfer lines
        transfer_origin = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        transfer_dest = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(transfer_origin.debit, 100.0)
        self.assertEqual(transfer_dest.credit, 100.0)
        # Check the invoices and bill are fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)
        self.assertEqual(self.bill1.amount_residual, 0.0)

    def test_reconcile_partial_with_transfer_without_write_off_from_payable(self):
        """
        Invoice 1 = 100, Invoice 2 = 50, Bill 1 = 100.
        The difference is 50, but with partial reconciliation,
        only 100 is transferred from payable to receivable, so no write-off is needed.
        Invoice 1 should be partially reconciled,
        and Invoice 2 and Bill 1 should be fully reconciled.
        """
        lines_to_reconcile = (
            self.invoice1.line_ids + self.invoice2.line_ids + self.bill1.line_ids
        ).filtered(
            lambda line: line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        )
        self.assertEqual(len(lines_to_reconcile), 3)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertTrue(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertTrue(wizard.allow_partial_reconcile)
        self.assertTrue(wizard.display_allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 50.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 5)
        new_move_lines = result_lines - lines_to_reconcile
        self.assertEqual(len(new_move_lines), 2)
        self.assertEqual(len(new_move_lines.move_id), 1)
        self.assertEqual(new_move_lines.move_id.move_type, "entry")
        # Check the transfer lines
        transfer_origin = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        transfer_dest = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(transfer_origin.debit, 100.0)
        self.assertEqual(transfer_dest.credit, 100.0)
        # Check the invoices and bill are reconciled as expected
        full_reconcile_lines = lines_to_reconcile - self.invoice1.line_ids
        self.assertTrue(all(line.reconciled for line in full_reconcile_lines))
        self.assertTrue(full_reconcile_lines.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 50.0)
        self.assertEqual(self.invoice2.amount_residual, 0.0)
        self.assertEqual(self.bill1.amount_residual, 0.0)

    def test_reconcile_partial_with_transfer_without_write_off_from_receivable(self):
        """
        Invoice 1 = 100, Bill 2 = 150.
        The difference is -50, but with partial reconciliation,
        only 100 is transferred from receivable to payable, so no write-off is needed.
        Invoice 1 should be fully reconciled,
        and Bill 2 should be partially reconciled.
        """
        lines_to_reconcile = (self.invoice1.line_ids + self.bill2.line_ids).filtered(
            lambda line: line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        )
        self.assertEqual(len(lines_to_reconcile), 2)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertTrue(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertTrue(wizard.allow_partial_reconcile)
        self.assertTrue(wizard.display_allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, -50.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 4)
        new_move_lines = result_lines - lines_to_reconcile
        self.assertEqual(len(new_move_lines), 2)
        self.assertEqual(len(new_move_lines.move_id), 1)
        self.assertEqual(new_move_lines.move_id.move_type, "entry")
        # Check the transfer lines
        transfer_origin = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        transfer_dest = new_move_lines.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        self.assertEqual(transfer_origin.credit, 100.0)
        self.assertEqual(transfer_dest.debit, 100.0)
        # Check the invoices and bill are reconciled as expected
        full_reconcile_lines = lines_to_reconcile - self.bill2.line_ids
        self.assertTrue(all(line.reconciled for line in full_reconcile_lines))
        self.assertTrue(full_reconcile_lines.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)
        self.assertEqual(self.bill2.amount_residual, 50.0)

    def test_reconcile_partial_with_transfer_and_write_off_from_payable(self):
        """
        Invoice 1 = 100, Invoice 2 = 50, Bill 1 = 100.
        The difference is 50, with partial reconciliation,
        100 is transferred from payable to receivable
        and 50 is written off with an expense account.
        All documents should be fully reconciled.
        """
        lines_to_reconcile = (
            self.invoice1.line_ids + self.invoice2.line_ids + self.bill1.line_ids
        ).filtered(
            lambda line: line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        )
        self.assertEqual(len(lines_to_reconcile), 3)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        wizard.allow_partial_reconcile = False
        self.assertTrue(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertEqual(wizard.balance_difference, 50.0)
        with self.assertRaisesRegex(
            UserError, "The total of write-off lines must balance the difference"
        ):
            wizard._action_reconcile()
        with Form(wizard) as wizard_form:
            with wizard_form.write_off_line_ids.new() as line:
                line.account_id = self.expense_account
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 7)  # 3 original + 2 transfer + 2 write-off
        new_move_lines = result_lines - lines_to_reconcile
        self.assertEqual(len(new_move_lines), 4)
        self.assertEqual(len(new_move_lines.move_id), 1)
        # Check the transfer lines
        transfer_origin = new_move_lines.filtered(
            lambda line: "Transfer to" in line.name
        )
        transfer_dest = new_move_lines.filtered(
            lambda line: "Transfer from" in line.name
        )
        self.assertEqual(
            transfer_origin.account_id, self.partner.property_account_payable_id
        )
        self.assertEqual(transfer_origin.debit, 100.0)
        self.assertEqual(
            transfer_dest.account_id, self.partner.property_account_receivable_id
        )
        self.assertEqual(transfer_dest.credit, 100.0)
        # Check the write-off lines
        write_off_lines = new_move_lines - transfer_origin - transfer_dest
        write_off_expense = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account
        )
        write_off_receivable = write_off_lines.filtered(
            lambda line: line.account_id == self.partner.property_account_receivable_id
        )
        self.assertEqual(len(write_off_expense), 1)
        self.assertEqual(write_off_expense.debit, 50.0)
        self.assertEqual(len(write_off_receivable), 1)
        self.assertEqual(write_off_receivable.credit, 50.0)
        # Check the invoices and bill are fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)
        self.assertEqual(self.invoice2.amount_residual, 0.0)
        self.assertEqual(self.bill1.amount_residual, 0.0)

    def test_reconcile_partial_with_transfer_and_write_off_from_receivable(self):
        """
        Invoice 1 = 100, Bill 2 = 150.
        The difference is -50, with partial reconciliation,
        100 is transferred from receivable to payable
        and 50 is written off with an expense account.
        All documents should be fully reconciled.
        """
        lines_to_reconcile = (self.invoice1.line_ids + self.bill2.line_ids).filtered(
            lambda line: line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        )
        self.assertEqual(len(lines_to_reconcile), 2)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        wizard.allow_partial_reconcile = False
        self.assertTrue(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertEqual(wizard.balance_difference, -50.0)
        with self.assertRaisesRegex(
            UserError, "The total of write-off lines must balance the difference"
        ):
            wizard._action_reconcile()
        with Form(wizard) as wizard_form:
            with wizard_form.write_off_line_ids.new() as line:
                line.account_id = self.expense_account
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 6)  # 2 original + 2 transfer + 2 write-off
        new_move_lines = result_lines - lines_to_reconcile
        self.assertEqual(len(new_move_lines), 4)
        self.assertEqual(len(new_move_lines.move_id), 1)
        # Check the transfer lines
        transfer_origin = new_move_lines.filtered(
            lambda line: "Transfer to" in line.name
        )
        transfer_dest = new_move_lines.filtered(
            lambda line: "Transfer from" in line.name
        )
        self.assertEqual(
            transfer_origin.account_id, self.partner.property_account_receivable_id
        )
        self.assertEqual(transfer_origin.credit, 100.0)
        self.assertEqual(
            transfer_dest.account_id, self.partner.property_account_payable_id
        )
        self.assertEqual(transfer_dest.debit, 100.0)
        # Check the write-off lines
        write_off_lines = new_move_lines - transfer_origin - transfer_dest
        write_off_expense = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account
        )
        write_off_payable = write_off_lines.filtered(
            lambda line: line.account_id == self.partner.property_account_payable_id
        )
        self.assertEqual(len(write_off_expense), 1)
        self.assertEqual(write_off_expense.credit, 50.0)
        self.assertEqual(len(write_off_payable), 1)
        self.assertEqual(write_off_payable.debit, 50.0)
        # Check the invoices and bill are fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)
        self.assertEqual(self.bill2.amount_residual, 0.0)

    def test_reconcile_with_write_off_and_no_transfer(self):
        """
        Invoice 1 = 100
        The difference is 100, with no transfer,
        100 is written off with an expense account.
        The invoice1 should be fully reconciled.
        """
        lines_to_reconcile = self.invoice1.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(len(lines_to_reconcile), 1)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertFalse(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertFalse(wizard.display_allow_partial_reconcile)
        self.assertFalse(wizard.allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 100.0)
        self.assertEqual(wizard.write_off_amount, 0.0)
        with self.assertRaisesRegex(
            UserError, "The total of write-off lines must balance the difference"
        ):
            wizard._action_reconcile()
        with Form(wizard) as wizard_form:
            with wizard_form.write_off_line_ids.new() as line:
                line.account_id = self.expense_account
                line.credit = 100.0
        self.assertEqual(wizard.write_off_amount, -100.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 3)  # 1 original + 2 write-off
        # Check the write-off lines
        write_off_lines = result_lines - lines_to_reconcile
        write_off_expense = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account
        )
        write_off_receivable = write_off_lines.filtered(
            lambda line: line.account_id == self.partner.property_account_receivable_id
        )
        self.assertEqual(len(write_off_expense), 1)
        self.assertEqual(write_off_expense.debit, 100.0)
        self.assertEqual(len(write_off_receivable), 1)
        self.assertEqual(write_off_receivable.credit, 100.0)
        # Check the invoice is fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)

    def test_reconcile_with_write_off_two_accounts(self):
        """
        Invoice 1 = 100
        The difference is 100, with no transfer,
        100 is written off with two expenses account.
        The invoice1 should be fully reconciled.
        """
        lines_to_reconcile = self.invoice1.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(len(lines_to_reconcile), 1)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertFalse(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertFalse(wizard.display_allow_partial_reconcile)
        self.assertFalse(wizard.allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 100.0)
        self.assertEqual(wizard.write_off_amount, 0.0)
        with self.assertRaisesRegex(
            UserError, "The total of write-off lines must balance the difference"
        ):
            wizard._action_reconcile()
        with Form(wizard) as wizard_form:
            with wizard_form.write_off_line_ids.new() as line:
                line.account_id = self.expense_account
                line.credit = 60.0
            # The second line will be automatically created to balance the difference
            with wizard_form.write_off_line_ids.new() as line:
                line.account_id = self.expense_account2
        self.assertEqual(wizard.write_off_amount, -100.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 4)  # 1 original + 3 write-off
        # Check the write-off lines
        write_off_lines = result_lines - lines_to_reconcile
        write_off_expense1 = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account
        )
        write_off_expense2 = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account2
        )
        write_off_receivable = write_off_lines.filtered(
            lambda line: line.account_id == self.partner.property_account_receivable_id
        )
        self.assertEqual(len(write_off_expense1), 1)
        self.assertEqual(write_off_expense1.debit, 60.0)
        self.assertEqual(len(write_off_expense2), 1)
        self.assertEqual(write_off_expense2.debit, 40.0)
        self.assertEqual(len(write_off_receivable), 1)
        self.assertEqual(write_off_receivable.credit, 100.0)
        # Check the invoice is fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)

    def test_reconcile_with_write_off_and_reconcile_model(self):
        """
        Invoice 1 = 100
        The difference is 100, with no transfer,
        100 is written off using a reconcile model
        with two lines of 40% and 60% on different expense accounts.
        The invoice1 should be fully reconciled.
        """
        lines_to_reconcile = self.invoice1.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(len(lines_to_reconcile), 1)
        wizard = self._create_reconcile_wizard(lines_to_reconcile)
        self.assertFalse(wizard.need_transfer)
        self.assertTrue(wizard.need_write_off)
        self.assertFalse(wizard.display_allow_partial_reconcile)
        self.assertFalse(wizard.allow_partial_reconcile)
        self.assertEqual(wizard.balance_difference, 100.0)
        self.assertEqual(wizard.write_off_amount, 0.0)
        with Form(wizard) as wizard_form:
            wizard_form.reconcile_model_id = self.reconcile_model_percentage
        self.assertEqual(len(wizard.write_off_line_ids), 2)
        self.assertEqual(wizard.write_off_amount, -100.0)
        result_lines = wizard._action_reconcile()
        self.assertEqual(len(result_lines), 4)  # 1 original + 3 write-off
        # Check the write-off lines
        write_off_lines = result_lines - lines_to_reconcile
        write_off_expense1 = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account
        )
        write_off_expense2 = write_off_lines.filtered(
            lambda line: line.account_id == self.expense_account2
        )
        write_off_receivable = write_off_lines.filtered(
            lambda line: line.account_id == self.partner.property_account_receivable_id
        )
        self.assertEqual(len(write_off_expense1), 1)
        self.assertEqual(write_off_expense1.debit, 60.0)
        self.assertEqual(len(write_off_expense2), 1)
        self.assertEqual(write_off_expense2.debit, 40.0)
        self.assertEqual(len(write_off_receivable), 1)
        self.assertEqual(write_off_receivable.credit, 100.0)
        # Check the invoice is fully reconciled
        self.assertTrue(all(line.reconciled for line in lines_to_reconcile))
        self.assertTrue(lines_to_reconcile.full_reconcile_id)
        self.assertEqual(self.invoice1.amount_residual, 0.0)
