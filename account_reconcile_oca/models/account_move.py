# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_first_non_locked_date(self):
        """Get the date of the move to reconcile, considering the lock
        dates defined in the company (user defined and tax dates).
        so that the date proposed is the lock date +1 day if there's a lock date,
        and the move date otherwise."""
        locks = []
        user_lock_date = self.company_id._get_user_fiscal_lock_date(self.journal_id)
        if user_lock_date:
            locks.append(user_lock_date)
        if self._affect_tax_report() and self.company_id.tax_lock_date:
            locks.append(self.company_id.tax_lock_date)
        lock_date = max(locks)
        if lock_date and self.date <= lock_date:
            return lock_date + timedelta(days=1)
        else:
            return self.date
