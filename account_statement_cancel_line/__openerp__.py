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
{
    'name': "Account Statement Cancel Line",
    'version': '0.3',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account',
        'account_statement_ext',
        'account_default_draft_move',
        'account_statement_base_completion',
    ],
    'description': """
        Account Statement Cancel Line

        This module allows to cancel one line of the statement without
        cancelling the whole thing.

        To do that, a state is added to the statement line.

        When the user confirms or cancels the whole statement, we keep the
        previous functionality, and then we change the state in all statement
        lines. We also add a warning if any lines are reconciled. If no lines
        are reconciled, we show a generic warning because the operation could
        take a long time.

        When the user confirms or cancels a statement line, we update the state
        of the line, and if necessary we update the state of the whole
        statement, too.

        If the user tries to cancel a line that is reconciled, we ask for
        confirmation before proceeding.
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': [
        'statement_view.xml',
        'wizard/cancel_statement_view.xml',
        'wizard/cancel_statement_line_view.xml',
    ],
    'demo_xml': [],
    'test': [
        'test/cancel_line.yml',
        'test/test_confirm_last_line_balance_check.yml',
        'test/test_confirm_last_line_no_balance_check.yml',
        'test/confirm_statement_no_double_moves.yml',
    ],
    'installable': False,
    'images': [],
    'license': 'AGPL-3',
}
