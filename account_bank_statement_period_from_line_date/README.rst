.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Use bank transaction date to determine move period
==================================================

By default, a bank statement in Odoo has its own period, and this period
will be assigned to all the moves generated from the bank statement lines,
regardless of their effective dates.

The desirability of this behaviour depends on the jurisdiction and may be
illegal.

This module was written to make sure that when reconciliation moves are
generated for a bank transaction, the period for the moves is determined from
the transaction (bank statement line) date, and not taken from the bank
statement.

Usage
=====

Just enter any bank statement with transactions on dates outside the accounting
period on the bank statement itself. When the moves are created, you will find
that these have the correct period set.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-statement-reconcile/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-statement-reconcile/issues/new?body=module:%20account_bank_statement_period_from_line_date%0Aversion:%201.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Contributors
------------

* Stefan Rijnhart <stefan@therp.nl>
* Ronald Portier <ronald@therp.nl>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
