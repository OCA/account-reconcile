This is a shared work between Akretion and Camptocamp in order to
provide:

- Reconciliation facilities for big volume of transactions.
- Setup different profiles of reconciliation by account.
- Each profile can use many methods of reconciliation.
- This module is also a base to create others reconciliation methods
  which can plug in the profiles.
- A profile a reconciliation can be run manually or by a cron.
- Monitoring of reconciliation runs with an history which keep track of
  the reconciled Journal items.

2 simple reconciliation methods are integrated in this module, the
simple reconciliations works on 2 lines (1 debit / 1 credit) and do not
allow partial reconciliation, they also match on 1 key, partner or
Journal item name. There is also an option for 'most recent move line'
or 'oldest move line' which is used to choose the move to be reconciled
if more than one is found.
