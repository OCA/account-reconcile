With this module, the *Reconcile* tab of the OCA bank statement
reconcile interface has a new behavior: when the bank statement line has
a partner, the *Reconcile* tab has 2 filters by default:

1.  filter on the Partner (native)
2.  filter **Payable or Receivable or Outstanding Payments/Receipts**
    (added)

That way, when the bank statement line has a partner and your VAT
accounts are reconciliable, you will not see the VAT lines by default in
the *Reconcile* tab, but only:

- the receivable accounts,
- the payable accounts,
- the journal items linked to a payment that have an account with type *Current Asset*.

When there is no partner on the bank statement line, the behavior is
unchanged: there are no filters by default.
