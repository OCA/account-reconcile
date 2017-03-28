[![Build Status](https://travis-ci.org/OCA/bank-statement-reconcile.svg?branch=10.0)](https://travis-ci.org/OCA/bank-statement-reconcile)
[![Coverage Status](https://coveralls.io/repos/OCA/bank-statement-reconcile/badge.png?branch=10.0)](https://coveralls.io/r/OCA/bank-statement-reconcile?branch=10.0)

Odoo modules for statements tasks (completion, reconciliation)
==============================================================

***Important notice: since version 8.0, the import feature has moved here: https://github.com/OCA/bank-statement-import***


__Version 8.0 and earlier :__

* Completion of infos (partner, account, ref,...) in statements.
* Provide methods for making automatic reconciliation in batch

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
[account_mass_reconcile](account_mass_reconcile/) | 10.0.1.0.0 | Mass Reconcile
[account_move_base_import](account_move_base_import/) | 10.0.1.0.0 | Journal Entry base import
[base_transaction_id](base_transaction_id/) | 10.0.1.0.0 | Base transaction id for financial institutes


Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_bank_statement_period_from_line_date](account_bank_statement_period_from_line_date/) | 8.0.1.0.0 (unported) | Use bank transaction (line) date to determine move period
[account_invoice_reference](account_invoice_reference/) | 8.0.1.0.1 (unported) | Invoices Reference
[account_mass_reconcile_ref_deep_search](account_mass_reconcile_ref_deep_search/) | 9.0.1.0.0 (unported) | Mass Reconcile Ref Deep Search
[account_mass_reconcile_transaction_ref](account_mass_reconcile_transaction_ref/) | 9.0.1.0.0 (unported) | Mass Reconcile Transaction Ref
[account_move_bankaccount_import](account_move_bankaccount_import/) | 9.0.1.0.0 (unported) | Journal Entry completion from bank account number
[account_move_so_import](account_move_so_import/) | 9.0.1.0.0 (unported) | Journal Entry Sale Order completion
[account_move_transactionid_import](account_move_transactionid_import/) | 9.0.1.0.0 (unported) | Journal Entry transactionID import
[account_operation_rule](account_operation_rule/) | 9.0.1.0.0 (unported) | Bank Statement Operation Rules
[account_payment_transaction_id](account_payment_transaction_id/) | 1.0 (unported) | Account Payment - Transaction ID
[account_reconcile_payment_order](account_reconcile_payment_order/) | 8.0.1.0.0 (unported) | Automatically reconcile all lines from payment orders
[account_statement_cancel_line](account_statement_cancel_line/) | 0.3 (unported) | Account Statement Cancel Line
[account_statement_completion_label](account_statement_completion_label/) | 0.1 (unported) | Bank statement completion from label
[account_statement_completion_voucher](account_statement_completion_voucher/) | 1.0 (unported) | Bank statement extension with voucher
[account_statement_ext](account_statement_ext/) | 1.3.6 (unported) | Bank statement extension and profiles
[account_statement_ext_point_of_sale](account_statement_ext_point_of_sale/) | 1.0.0 (unported) | Bank statement extension and profiles for Point of Sale
[account_statement_ext_voucher](account_statement_ext_voucher/) | 1.0 (unported) | Bank statement extension with voucher
[account_statement_no_invoice_import](account_statement_no_invoice_import/) | 0.1 (unported) | account bank statement no invoice import
[account_statement_one_move](account_statement_one_move/) | 0.1 (unported) | Bank statement one move
[account_statement_operation_multicompany](account_statement_operation_multicompany/) | 8.0.0.2.0 (unported) | Fix multi-company issue on Statement Operation Templates
[account_statement_regex_account_completion](account_statement_regex_account_completion/) | 0.1 (unported) | Account Statement Regex Account Completion addon

[//]: # (end addons)
