.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================================
Account Skip Bank Reconciliation
================================

This module allows to exclude from bank statement reconciliation
all journal items of a specific reconcilable account.

Usually, you would want to that in accounts like the
`Goods Received Not Invoiced`, which are required to be reconcilable
to be able to have proper traceability in stock received but
their reconciliation is done using the `account_mass_reconcile` module.

Usage
=====

To use this module, you need to:

#. Go to  `Invoicing / Configuration / Accounting / Charts of Accounts`
   and open a reconcilable account.
#. In that account, select or not the `Exclude from Bank Reconciliation` option.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-reconcile/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Miquel Raïch <miquel.raich@eficent.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
