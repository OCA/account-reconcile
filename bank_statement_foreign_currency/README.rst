.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================
Bank Statement Foreign Currency
===============================

This module makes visible the currency columns in the bank statements lines.

Notice that all banks will provide the amounts in the account's main
currency and in the foreign currency. You are not supposed to rely on
Odoo's currency rate of the moment. The exchange rate is given by the bank.

For example, You buy a widget in Amazon.com for $100.

You can see in your statement:
Amazon.com -80€ (-$100)

Then you enter exactly this in Odoo's bank statement. The rate 80€/$100 is the
rate that the bank applied to the payment you made in USD in Amazon.com,
because your bank account is held in EUR. You need the $100 to be able to
reconcile with the invoice, and you need the €80 because that's what hit your
bank.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-reconcile/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------
* Miquel Raïch <miquel.raich@eficent.com>
* Luis M. Ontalba <luis.martinez@tecnativa.com>


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
