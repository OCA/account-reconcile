Adds reconciliation status tracking to bank statements.

In Odoo 18, bank reconciliation is line-oriented — each statement line is
reconciled independently. This module adds an aggregated view so you can tell
at a glance which statements are done and which still need work.

Two fields are added to `account.bank.statement`:

- **Reconciliation Status**: Not Started / In Progress / Fully Reconciled
- **First Fully Reconciled On**: timestamp set once when all lines are first
  reconciled — never cleared, so you can detect if someone later undoes a
  reconciliation

The list view shows a colored badge, and the search view adds filters to
quickly find statements that need attention or that changed after being closed.
