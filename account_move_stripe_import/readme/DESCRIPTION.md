This module imports the Stripe payouts paid to your bank account as
journal entries, to reconcile them with the customer invoices and the
bank statement.

For each Stripe payout, the import creates one journal entry in the
Stripe journal, with:

- one line per Stripe balance transaction of the payout (payments on the
  credit side, refunds on the debit side);
- one fee line per type of Stripe fee, on the commission account of the
  journal;
- the payout counterpart, on the account of the journal.

The reference of the journal entry is the id of the Stripe payout. A
payout already imported is never imported again, and a payout still
pending or in transit is imported once paid.
