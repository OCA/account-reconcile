# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_import_type_selection(self):
        """Has to be inherited to add parser"""
        res = super(AccountJournal, self)._get_import_type_selection()
        res.append(('generic_csvxls_transaction',
                    'Generic .csv/.xls based on SO transaction ID'))
        return res
