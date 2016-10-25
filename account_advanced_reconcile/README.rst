.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :alt: License: AGPL-3

Advanced Reconcile
==================

This module was written to extend the functionality of **Easy Reconcile** (`account_easy_reconcile`).

In addition to the features implemented in **Easy Reconcile** (`account_easy_reconcile`), which are:
 - reconciliation facilities for big volume of transactions
 - setup different profiles of reconciliation by account
 - each profile can use many methods of reconciliation
 - this module is also a base to create others reconciliation methods
    which can plug in the profiles
 - a profile a reconciliation can be run manually or by a cron
 - monitoring of reconcilation runs with an history

It implements a basis to created advanced reconciliation methods in a few lines
of code.

Typically, such a method can be:
 - Reconcile Journal items if the partner and the ref are equal
 - Reconcile Journal items if the partner is equal and the ref
   is the same than ref or name
 - Reconcile Journal items if the partner is equal and the ref
   match with a pattern

And they allows:
 - Reconciliations with multiple credit / multiple debit lines
 - Partial reconciliations
 - Write-off amount as well

A method is already implemented in this module, it matches on items:
 - Partner
 - Ref on credit move lines should be case insensitive equals to the ref or
   the name of the debit move line

The base class to find the reconciliations is built to be as efficient as
possible.

So basically, if you have an invoice with 3 payments (one per month), the first
month, it will partial reconcile the debit move line with the first payment,
the second month, it will partial reconcile the debit move line with 2 first
payments, the third month, it will make the full reconciliation.

This module is perfectly adapted for E-Commerce business where a big volume of
move lines and so, reconciliations, are involved and payments often come from
many offices.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-statement-reconcile/issues>`_.

In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-statement-reconcile/issues/new?body=module:%20account_advanced_reconcile%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Frédéric Clementi <frederic.clementi@camptocamp.com>
* Vincent Renaville <vincent.renaville@camptocamp.com>
* Pedro M. Baeza <pedro.baeza@gmail.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Rudolf Schnapka <rs@techno-flex.de> (German translations)
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org
