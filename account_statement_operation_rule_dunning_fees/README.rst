.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Bank Statement Operation Rules with Dunning Fees
================================================

Extends the *Bank Statement Operation Rules* with a new rule, the
**Dunning Fees** rule. It allows to automatically create a write-off
entry for the amount paid by the customers when they received dunning
fees (using the **Account Credit Control** module).

Configuration
-------------

As this module aims to automatize the ``Statement Operation Templates``,
you first want to ensure that you have an operation configured for the
dunning fees.
You can find them in ``Invoicing > Configuration > Miscellaneous >
Statement Operation Templates``. An example of operation is (the account
is where the amount received for the dunning fees will be input):

=================== ========================== ======= ============
Account             Amount Type                Amount  Label
=================== ========================== ======= ============
Depends of the l10n Percentage of open balance 100.0 % Dunning Fees
=================== ========================== ======= ============

The configuration of the rules themselves happens in ``Invoicing >
Configuration > Miscellaneous > Statement Operation Rules``.

There is no conditions to setup on this rule. It will be applied if the
amount in the bank statement line is above the journal entries amount
and if the difference is comprised in the amount of the dunning fees for
the journal entries.

Example:

======================= ======
Document                Amount
======================= ======
Journal Entry (invoice) 100.-
Dunning Fees no1        5.-
Dunning Fees no2        10.-
Dunning Fees no3        15.-
======================= ======

The customer received 3 times dunning fees, with a increasing amount.
The customer might pay from 100.- to 115.-. The difference between
100.- and what the customer paid above goes to the write-off account
configured on the operation. If the customer pays 99.- or 116.-, the
Dunning Fees rule is not valid and the other rules will be evaluated.

.. note:: The Dunning Fees rule must be placed before the Roundings
          rules, otherwise the fees might be confused with roundings.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/8.0

Dependencies
------------

This module only works with the ``account_credit_control_dunning_fees``
module in the project: https://github.com/OCA/account-financial-tools

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

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
