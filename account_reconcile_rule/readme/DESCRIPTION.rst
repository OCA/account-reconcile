This module complements the Reconciliation of the bank statements.  When
the bank statement matches one or more journal entry for a line and
there is a remaining balance, Odoo proposes you to click on buttons that
will generate write-off entries according to pre-configured *Reconciliation
Models*. The aim of this module is to automatically click
for you on these buttons (i.e. create the write-off journal entries)
when some rules are respected, rules that you can configure.

It contains 2 types of rules (but can be extended with additional rules),
described below:

Roundings
  The most basic rule: when the remaining balance is within a range, 1
  or more operations are applied.

Currencies
  When the remaining balance is within a range and the currency of all
  the lines is the same but different from the company's, and the amount
  currency is the same, 1 or more operations are applied.
