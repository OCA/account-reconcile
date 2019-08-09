[![Build Status](https://travis-ci.org/OCA/account-reconcile.svg?branch=8.0)](https://travis-ci.org/OCA/account-reconcile)
[![Coverage Status](https://coveralls.io/repos/OCA/account-reconcile/badge.png?branch=8.0)](https://coveralls.io/r/OCA/account-reconcile?branch=8.0)

Odoo account reconciliation modules (statements, data completion,...)
=====================================================================

***Important notice: since version 8.0, the import feature has moved here: https://github.com/OCA/bank-statement-import***


__Version 8.0 and later :__

* Completion of infos (partner, account, ref,...) in statements.
* Provide methods for making automatic reconciliation in batch.

Other features can be found in those repository:
* https://github.com/OCA/bank-payment
* https://github.com/OCA/bank-statement-import

__Version 7.0 and earlier :__

* Importing bank statements.
* Complete partner on these statements.
* Provide methods for making automatic reconciliation.


[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[account_advanced_reconcile](account_advanced_reconcile/) | 8.0.1.0.0 | Reconcile: with multiple lines / partial / with writeoffs
[account_bank_statement_period_from_line_date](account_bank_statement_period_from_line_date/) | 8.0.1.0.0 | Use bank transaction (line) date to determine move period
[account_easy_reconcile](account_easy_reconcile/) | 8.0.1.3.1 | Easy Reconcile
[account_invoice_reference](account_invoice_reference/) | 8.0.1.0.1 | Invoices Reference
[account_reconcile_payment_order](account_reconcile_payment_order/) | 8.0.1.0.1 | Automatically reconcile all lines from payment orders
[account_reconcile_prepare_account](account_reconcile_prepare_account/) | 8.0.1.0.0 | Assign bank transactions to accounts before reconciliation
[account_statement_operation_multicompany](account_statement_operation_multicompany/) | 8.0.0.2.0 | Fix multi-company issue on Statement Operation Templates
[account_statement_operation_rule](account_statement_operation_rule/) | 8.0.1.0.0 | Bank Statement Operation Rules
[account_statement_operation_rule_dunning_fees](account_statement_operation_rule_dunning_fees/) | 8.0.1.0.0 | Bank Statement Operation Rules with Dunning Fees
[base_transaction_id](base_transaction_id/) | 8.0.1.0.0 | Base transaction id for financial institutes


Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_advanced_reconcile_bank_statement](account_advanced_reconcile_bank_statement/) | 1.0.0 (unported) | Advanced Reconcile Bank Statement
[account_advanced_reconcile_transaction_ref](account_advanced_reconcile_transaction_ref/) | 1.0.1 (unported) | Advanced Reconcile Transaction Ref
[account_payment_transaction_id](account_payment_transaction_id/) | 1.0 (unported) | Account Payment - Transaction ID
[account_statement_bankaccount_completion](account_statement_bankaccount_completion/) | 1.0.1 (unported) | Bank statement completion from bank account number
[account_statement_base_completion](account_statement_base_completion/) | 1.0.3 (unported) | Bank statement base completion
[account_statement_base_import](account_statement_base_import/) | 1.2 (unported) | Bank statement base import
[account_statement_cancel_line](account_statement_cancel_line/) | 0.3 (unported) | Account Statement Cancel Line
[account_statement_commission](account_statement_commission/) | 1.0 (unported) | Bank statement import - commissions
[account_statement_completion_label](account_statement_completion_label/) | 0.1 (unported) | Bank statement completion from label
[account_statement_completion_voucher](account_statement_completion_voucher/) | 1.0 (unported) | Bank statement extension with voucher
[account_statement_ext](account_statement_ext/) | 1.3.6 (unported) | Bank statement extension and profiles
[account_statement_ext_point_of_sale](account_statement_ext_point_of_sale/) | 1.0.0 (unported) | Bank statement extension and profiles for Point of Sale
[account_statement_ext_voucher](account_statement_ext_voucher/) | 1.0 (unported) | Bank statement extension with voucher
[account_statement_no_invoice_import](account_statement_no_invoice_import/) | 0.1 (unported) | account bank statement no invoice import
[account_statement_one_move](account_statement_one_move/) | 0.1 (unported) | Bank statement one move
[account_statement_regex_account_completion](account_statement_regex_account_completion/) | 0.1 (unported) | Account Statement Regex Account Completion addon
[account_statement_so_completion](account_statement_so_completion/) | 0.1 (unported) | Bank statement Sale Order completion
[account_statement_transactionid_completion](account_statement_transactionid_completion/) | 1.0 (unported) | Bank statement completion from transaction ID
[account_statement_transactionid_import](account_statement_transactionid_import/) | 1.0 (unported) | Bank statement transactionID import

[//]: # (end addons)
