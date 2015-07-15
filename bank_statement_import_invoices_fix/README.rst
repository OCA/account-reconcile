.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Bank statement import invoices fix
==================================

This module was written to extend the functionality of importing invoices as bank statement lines.
It inverts values of "communication" and "reference" fields.

This way, when lines are imported the reference goes to the communication field (instead of
reference of the bank statement line) in order to have a default proposal from the system during
the reconciliation process.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-statement-reconcile/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-statement-reconcile/issues/new?body=module:%20bank_statement_import_invoices_fix%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Damien Crier <damien.crier@camptocamp.com>
* Frédéric Clementi <frederic.clementi@camptocamp.com>

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
