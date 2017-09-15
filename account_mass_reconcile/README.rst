.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

======================
Account Mass Reconcile
======================

This is a shared work between Akretion and Camptocamp
in order to provide:

- Reconciliation facilities for big volume of transactions.
- Setup different profiles of reconciliation by account.
- Each profile can use many methods of reconciliation.
- This module is also a base to create others
  reconciliation methods which can plug in the profiles.
- A profile a reconciliation can be run manually
  or by a cron.
- Monitoring of reconciliation runs with an history
  which keep track of the reconciled Journal items.

2 simple reconciliation methods are integrated
in this module, the simple reconciliations works
on 2 lines (1 debit / 1 credit) and do not allow
partial reconciliation, they also match on 1 key,
partner or Journal item name.

Usage
=====

Go to 'Invoicing / Adviser / Mass Automatic Reconcile' to start a new mass
reconcile.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-statement-reconcile/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------
* Sébastien Beau <sebastien.beau@akretion.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Vincent Renaville <vincent.renaville@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Nicolas Bessis <nicolas.bessi@camptocamp.com>
* Pedro M.Baeza <pedro.baeza@gmail.com>
* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Ecino <ecino@compassion.ch>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Rudolf Schnapka <rs@techno-flex.de>
* Florian Dacosta <florian.dacosta@akretion.com>
* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Frédéric Clémenti <frederic.clementi@camptocamp.com>
* Damien Crier <damien.crier@camptocamp.com>
* Akim Juillerat <akim.juillerat@camptocamp.com>

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
