# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{'name': 'Invoices Reference',
 'version': '8.0.1.0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'category',
 'complexity': "easy",
 'depends': ['account',
             ],
 'description': """
Invoices Reference
==================

Aims to simplify the "references" fields on the invoices.

We observed difficulties for the users to file the references (name,
origin, free reference) and above all, to understand which field will be
copied in the reference field of the move and move lines.

The approach here is to state simple rules with one concern: consistency.
The reference of the move lines must be the number of the document at their
very origin (number of a sales order, of an external document like a supplier
invoice, ...). The goal is for the accountant to be able to trace to the
source document from a ledger).
The description of a line should always be... well, a description. Not a number
or a cryptic reference.

It particularly fits with other modules of the bank-statement-reconcile series
as account_advanced_reconcile_transaction_ref.

Fields
------

Enumerating the information we need in an invoice, we find that the
mandatory fields are:

* Invoice Number
* Description
* Internal Reference ("our reference")
* External Reference ("customer or supplier reference")
* Optionally, a technical transaction reference (credit card payment gateways,
  SEPA, ...)

Now, on the move lines:

* Name
* Reference
* Optionally, a technical transaction reference (added by the module
  `base_transaction_id`)

Let's see how the information will be organized with this module.

Customers Invoices / Refunds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    +-----------------+-----------------+------------------------------+
    | Information     | Invoice field   | Instead of (in base modules) |
    +=================+=================+==============================+
    | Invoice number  | Invoice number  | Invoice number               |
    +-----------------+-----------------+------------------------------+
    | Description     | Name            | --                           |
    +-----------------+-----------------+------------------------------+
    | Internal Ref    | Origin          | Origin                       |
    +-----------------+-----------------+------------------------------+
    | External Ref    | Reference       | Name                         |
    +-----------------+-----------------+------------------------------+

Information propagated to the move lines:

    +-----------------+------------------------------------+
    | Move line field | Invoice field                      |
    +=================+====================================+
    | Description     | Name                               |
    +-----------------+------------------------------------+
    | Reference       | Origin, or Invoice number if empty |
    +-----------------+------------------------------------+


Supplier Invoices / Refunds
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supplier invoices have an additional field `supplier_invoice_number`
that we consider as redundant with the reference field.  This field is kept
and even set as mandatory, while the reference field is hidden.

    +-----------------+-----------------+------------------------------+
    | Information     | Invoice field   | Instead of (in base modules) |
    +=================+=================+==============================+
    | Invoice number  | Invoice number  | Invoice number               |
    +-----------------+-----------------+------------------------------+
    | Description     | Name            | --                           |
    +-----------------+-----------------+------------------------------+
    | Internal Ref    | Origin          | Origin                       |
    +-----------------+-----------------+------------------------------+
    | External Ref    | Supplier number | Supplier number              |
    +-----------------+-----------------+------------------------------+

The reference field is hidden when the reference type is "free reference",
because it is already filed in the Supplier invoice number.

Information propagated to the move lines:

    +-----------------+---------------------------------------------+
    | Move line field | Invoice field                               |
    +=================+=============================================+
    | Description     | Name                                        |
    +-----------------+---------------------------------------------+
    | Reference       | Supplier number, or Invoice number if empty |
    +-----------------+---------------------------------------------+

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['account_invoice_view.xml',
          ],
 'test': ['test/out_invoice_with_origin.yml',
          'test/out_invoice_without_origin.yml',
          'test/in_invoice_with_supplier_number.yml',
          'test/in_invoice_without_supplier_number.yml',
          'test/out_refund_with_origin.yml',
          'test/out_refund_without_origin.yml',
          'test/in_refund_with_supplier_number.yml',
          'test/in_refund_without_supplier_number.yml',
          'test/supplier_invoice_number.yml',

          ],
 'installable': True,
 'auto_install': False,
 }
