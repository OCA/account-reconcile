===============================
Customer Payment Reconciliation
===============================

This module allows **partial payment settlement** for customers across multiple invoices.
It is designed to manage scenarios where:
- Customers have outstanding invoices.
- Customers want to make **partial payments** based on their available payment made in bulk.
- Customers make **advance payments** that can be distributed across their open invoices.

Features
========
- New button: **Partial Amount Settle** on the customer form.
- Allows selecting which invoices to partially pay.
- Supports payment settlement based on available customer credit.
- Supports advance payments that can be applied to future invoices.
- Handles multi-invoice partial payments smoothly.
- Wizard interface to assist with partial settlement selection.

Usage
=====
1. Go to **Customers > Customers**.
2. Open a customer who has open invoices.
3. Click on the **Partial Amount Settle** button.
4. In the wizard, select the invoices and enter the payment amounts.
5. Validate to apply the partial payments across the selected invoices.

Credits
=======

Authors
-------
* Areterix Technologies

Contributors
------------
* Umar Maniar, (Areterix Technologies)

Maintainers
-----------
This module is maintained by Areterix Technologies.

Bug Tracker
===========
Bugs are tracked on `GitHub Issues <https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPOSITORY/issues>`_.
In case of problems, please log them there.

To contribute to this module, please visit:
https://github.com/umaniar-plus/YOUR-REPOSITORY

Roadmap
=======
- Add multi-currency support.
- Add payment reconciliation reporting.
- Improve user feedback for settlement errors.

Known Issues
============
- Currently supports only customer invoices.
- Vendor bill partial reconciliation not yet implemented.
