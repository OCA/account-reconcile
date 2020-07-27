
Adds transaction ID to invoice and sale models and views.

On Sales order, you can specify the transaction ID used for the payment and it
will be propagated to the invoice (even if made from packing).
This is mostly used for e-commerce handling.

You can then add a mapping on that SO field to save the e-commerce financial
Transaction ID into the Odoo sale order field.

The main purpose is to ease the reconciliation process and be able to find the partner
when importing the bank statement.
