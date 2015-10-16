.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Base transaction id for financial institutes
============================================

Adds transaction id to invoice and sale models and views.

On Sales order, you can specify the transaction ID used
for the payment and it will be propagated to the invoice (even if made from packing).
This is mostly used for e-commerce handling.

You can then add a mapping on that SO field to save the e-commerce financial
Transaction ID into the Odoo sale order field.

The main purpose is to ease the reconciliation process and be able to find the partner
when importing the bank statement.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-statement-reconcile/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Pedro Baeza <pedro.baezo@gmail.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>

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
