.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Account move base import
========================

This module is a grouping of 7.0/8.0 modules, used to import accounting files
and completing them automatically:

* account_statement_base_completion
* account_statement_base_import
* account_statement_commission
* account_statement_ext

The main change is that, in order to import financial data, this information
is now imported directly as a Journal Entry.

Most of the information present in the "statement profile" is now located in
the account journal (with 2 boolean parameters which allows to use
this journal for importation and/or auto-completion).

Financial data can be imported using a standard .csv or .xls file (you'll find
it in the 'data' folder). It respects the journal to pass the entries.

This module can handle a commission taken by the payment office and has the
following format:
* __date__: date of the payment
* __amount__: amount paid in the currency of the journal used in the
importation
* __label__: the comunication given by the payment office, used as
communication in the generated entries.

Another column which can be used is __commission_amount__, representing
the amount for the commission taken by line.

Afterwards, the goal is to populate the journal items with information that
the bank or office gave you. For this, completion rules can be specified by
journal.

Some basic rules are provided in this module:

1) Match from statement line label (based on partner field 'Bank Statement
Label')
2) Match from statement line label (based on partner name)
3) Match from statement line label (based on Invoice reference)

Feel free to extend either the importation method, the completion method, or
both.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/10.0

Known issues / Roadmap
======================

* As for now, the module does not handle multicurrency imports.

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

* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Sébastien Beau <sebastien.beau@akretion.com>
* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>

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
