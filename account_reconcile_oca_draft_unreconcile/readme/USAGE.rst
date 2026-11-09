When a journal entry (invoice, bill, payment, payslip entry...) reconciled with a
bank statement line is reset to draft, the reconciliation of that statement line is
undone so that it shows up again as to reconcile, and a message is posted on the
statement line (*Chatter* tab of the reconciliation view). As the statement line is
always reconciled as a whole, the other entries matched with it are unreconciled as
well.

Only the journals using the *Edit Move* reconcile mode (the default one) are
covered: with *Keep Suspense Accounts*, the reconciliation is done in a separate
journal entry that is not linked to the statement line.
