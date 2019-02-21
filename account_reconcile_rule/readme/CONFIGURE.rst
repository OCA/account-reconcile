As this module aims to automatize the ``Reconciliation Models``,
you first want to ensure that you have at least one model configured.
You can find them in ``Invoicing > Dashboard > Bank card > More
> Reconciliation Models``. An example of a common operation is:

=================== ========================== ======= ========
Account             Amount Type                Amount  Label
=================== ========================== ======= ========
Depends of the l10n Percentage of open balance 100.0 % Rounding
=================== ========================== ======= ========

The configuration of the rules themselves happens in ``Invoicing >
Dashboard > Bank card > More > Reconciliation Rules``. Refer to
the description of the types of rules above in case of doubt. The form
is divided in 2 parts: **Rule** and **Result**. The rule part is where
you will set the conditions and the result part is what operations will
be done if the conditions are valid.

For the **Roundings** rules, you will set a min. and a max. amount. It
can be negative or positive. The amount is compared to the remaining
balance when lines are matched in the bank statement.  Example: if you
want to create a move line in a loss account when you received 1.- not
enough, you can create a rule with an min. amount of -1.0 and a max.
amount of 0.0.

For the **Currencies** rules, the min. and max. amount have the same
properties, but you will also set the currencies for which the rule
applies. Setting the currency allows to configure different amounts
according to the currencies.

Only the first rule matching the current situation is used, so if you
have several rules overlapping for some reason, be sure to order them
appropriately in the list view.
