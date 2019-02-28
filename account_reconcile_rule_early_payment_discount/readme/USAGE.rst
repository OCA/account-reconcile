1. Look at  ``account_early_payment_discount``
module in the project: https://github.com/OCA/account-payment
to configure payment terms with an early payment discount.

-----

2. Configure some ``Reconciliation Models`` in
``Invoicing > Dashboard > Bank Card > Reconciliation Models``

.. image:: docs/operation_rule_menu.png

.. image:: docs/rule_model.png

-----

3. Then configure a new Reconciliation Rule in
``Invoicing > Dashboard > Bank Card > Reconciliation Rules``

.. image:: docs/rule.png

-----

4. Then during reconciliation, if a bank statement line matches an invoice which has a
payment term configured with early payment discount, this rule will verify if
the remaining balance respects the early payment discount rules
(discount percentage and payment delay).
If true, the remaining balance will be automatically reconciled in the configured account.

.. image:: docs/reconcilation.png
