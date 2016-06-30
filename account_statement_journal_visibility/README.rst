.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Control Statement Visibility Based On Groups
============================================

This module add functionality to limit visibility of:

1. Bank Statement based on *Allowed Groups on Bank Statement* setting on each journal
2. Cash Register based on *Allowed Groups on Cash Register* setting on each journal

This module also limit journal selection on:

1. Bank Statement based on *Allowed Groups on Bank Statement* setting on each journal
2. Cash Register based on *Allowed Groups on Cash Register* setting on each journal

This feature would be handy if company has several bank or cash journal and has different
user for each journal

**CASE STUDY**

Company A has 2 branches with seperate petty cash account. Each petty cash has it own user.
Each user does not has authorization to see other cast register data.

1. Create group (1) *Branch A*, and (2) *Branch B*
2. Assign *User A* into *Branch A* group and *User B* into *Branch B* group
3. Open *Petty Cash Branch A* journal data. Select *Branch A* group into *Allowed Groups on Cash Register*
3. Open *Petty Cash Branch B* journal data. Select *Branch B* group into *Allowed Groups on Cash Register*

With Odoo default procedure Odoo implementor has to hack into Record Rules and/or modified/extend
Cash Register/Bank Statement view.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/bank-statement-reconcile
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Control Statement Visibility Based On Groups*
6.  Install the module

Configuration
=============

**To configure bank statement visibility and bank statement journal selection, you need to:**

1. Open journal data (with Bank type)
2. Click on *Entry Controls* tab
3. If you would like to limit visibility of bank statement with this journal, you have to give authorization to intended group(s) by selection them on *Allowed Groups on Bank Statement* field

Note:
Empty selection on *Allowed Groups on Bank Statement* will give default visibility according Odoo record rules


**To configure cash register visibility and cash register journal selection, you need to:**

1. Open journal data (with Cash type)
2. Click on *Entry Controls* tab
3. If you would like to limit visibility of cash register with this journal, you have to give authorization to intended group(s) by selection them on *Allowed Groups on Cash Register* field

Note:
Empty selection on *Allowed Groups on Bank Statement* will give default visibility according Odoo record rules

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/98/8.0


Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-statement-reconcile/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
bank-statement-reconcile/issues/new?body=module:%20
account_statement_journal_visibility%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

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
