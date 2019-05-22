This module extends account_mass_reconcile to add a checkbox allowing only
selected mass reconcile to be run automatically after each other (using
multiple calls) by a scheduled task, instead of the existing scheduled task
running either everything or only the oldest mass reconcile that was run,
in a single call.
