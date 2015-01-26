Account Statement Operation Multi-company
=========================================

This module fixes Odoo bug n°4706 *account.statement.operation.template is not multi-company aware* https://github.com/odoo/odoo/issues/4706 that OpenERP S.A. doesn't want to fix because it requires an update of the datamodel in version 8 and this is against their rules for fixes in the stable branch.

Usage
=====

This module adds a read-only *company_id* field on the object *account.statement.operation.template* and a multi-company record rule.

Roadmap
=======

The bug which is solved by this module is supposed to be fixed in version 9, so this module will not be ported to future versions.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
