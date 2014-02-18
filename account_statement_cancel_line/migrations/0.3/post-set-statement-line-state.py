# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone                                                  #
#   Copyright 2014 Camptocamp SA                                              #
#                                                                             #
#   Inspired by module account_banking by EduSense BV, Therp BV, Smile        #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__name__ = ("account.bank.statement.line:: set new field 'state' to "
            "confirmed for all statement lines belonging to confirmed "
            "statements")


def migrate(cr, version):
    """This module adds the field state to the statement line. Here we set it
    correctly on existing statements. The names, and so this migration, are
    intentionally kept in sync with the account_banking module."""
    cr.execute("UPDATE account_bank_statement_line as sl "
               " SET state = 'confirmed'"
               " FROM account_bank_statement as s "
               " WHERE sl.statement_id = s.id "
               " AND s.state = 'confirm' "
               )
