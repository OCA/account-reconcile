.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Module name
===========

By default, a bank statement in Odoo has its own period, and this period
will be assigned to all the moves generated from the bank statement lines,
regardless of their effective dates.

The desirability of this behaviour depends on the jurisdiction and may be
illegal.

This module was written to make sure that when reconciliation moves are
generated for a bank transaction, the period for the moves is determined from
the transaction (bank statement line) date, and not taken from the bank
statement.

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
