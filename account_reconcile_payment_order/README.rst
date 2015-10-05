.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3
Reconcile payment orders
========================

Payment orders that show up as as one big transaction can be difficult for the accounting to handle if a transfer acount is used. In this case, we need to reconcile this transaction with possibly hunderds of move lines, which can be a bit tiresome. This module tries to recognize transactions deriving from payment orders and propose the unreconciled move lines from this payment order.

Usage
=====

It should just work. What the module does is to search for a payment order in state 'sent' that has the same amount as the statement line, and the same bank account than the statement.

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* it would be good to check references too, but at least the bank in use here changes some characters, so this doesn't seem to be a general solution.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-statement-reconcile/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-statement-reconcile/issues/new?body=module:%20account_reconcile_payment_order%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
