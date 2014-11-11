.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Bank Statement Operation Rules
==============================

This module complements the Reconciliation of the bank statements.  When
the bank statement matches one or more journal entry for a line and
there is a remaining balance, Odoo proposes you to click on buttons that
will generate write-off entries according to pre-configured *Statement
Operation Templates*. The aim of this module is to automatically click
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


Configuration
-------------

As this module aims to automatize the ``Statement Operation Templates``,
you first want to ensure that you have at least one operation configured.
You can find them in ``Invoicing > Configuration > Miscellaneous >
Statement Operation Templates``. An example of a common operation is:

=================== ========================== ======= ========
Account             Amount Type                Amount  Label
=================== ========================== ======= ========
Depends of the l10n Percentage of open balance 100.0 % Rounding
=================== ========================== ======= ========

The configuration of the rules themselves happens in ``Invoicing >
Configuration > Miscellaneous > Statement Operation Rules``. Refer to
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

Usage
-----

When you use the *Reconcile* button of a bank statement, Odoo
automatically proposes you matching journal entries for each statement
line.  This module automatically adds journal entries generated from the
*Statement Operation Templates* if a rule matches with the current
situation, so there is nothing special to do once the rules are
configured.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/8.0

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
whose mission is to support the collaborative development of Odoo
features and promote its widespread use.

To contribute to this module, please visit
http://odoo-community.org.
