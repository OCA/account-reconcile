.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

=======================================
Account Mass Reconcile by Purchase Line
=======================================

This module extends the functionality of acccount_mass_reconcile and
allow an user to reconcile debits and credits of an Account
using the PO Line and Product as key fields. This type of
reconciliation is to be used in the context of the Perpetual Inventory
accounting system, with the accrual account '*Goods Received Not Invoiced*'.

Usage
=====

To use this module, you need to:

* Go to 'Accounting / Adviser / Mass Automatic Reconcile'.

* Create a new reconciliation profile, and select a new configuration entry
  with type 'Advanced. Product, purchase order line.'.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-statement-reconcile/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Miquel Raïch <miquel.raich@eficent.com>
* Lois Rilo <lois.rilo@eficent.com>

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
