This module is a grouping of 7.0/8.0 modules, used to import accounting files
and completing them automatically:

* account_statement_base_completion
* account_statement_base_import
* account_statement_commission
* account_statement_ext

The main change is that, in order to import financial data, this information
is now imported directly as a Journal Entry.

Most of the information present in the "statement profile" is now located in
the account journal (with 2 boolean parameters which allows to use
this journal for importation and/or auto-completion).

Financial data can be imported using a standard .csv or .xls file (you'll find
it in the 'data' folder). It respects the journal to pass the entries.

This module can handle a commission taken by the payment office and has the
following format:
* __date__: date of the payment
* __amount__: amount paid in the currency of the journal used in the
importation
* __label__: the comunication given by the payment office, used as
communication in the generated entries.

Another column which can be used is __commission_amount__, representing
the amount for the commission taken by line.

Afterwards, the goal is to populate the journal items with information that
the bank or office gave you. For this, completion rules can be specified by
journal.

Some basic rules are provided in this module:

1) Match from statement line label (based on partner field 'Bank Statement
Label')
2) Match from statement line label (based on partner name)
3) Match from statement line label (based on Invoice reference)

Feel free to extend either the importation method, the completion method, or
both.
