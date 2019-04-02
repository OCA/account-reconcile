When using Odoo PoS, each operation (order) generates a journal item for its
payment. But When dealing with non cash methods (for example, credit card
payment through a terminal), later conciliation with bank statements is
very difficult as banks usually includes all the payment of a period (normally,
among the day) together in only one bank statement line.

This module helps to match automatically these lines on reconciliation widget
for only accepting the proposition without having to select individually
each line that belongs to that session.

In contrast to other solutions to this problem, this one avoids the burden of
generating extra entries that groups the amount transferring between accounts,
affecting general performance, increasing database size, or having side effects
(like incorrect partner ledger balancing).
