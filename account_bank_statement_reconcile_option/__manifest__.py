# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Account Bank Statement Reconcile Options',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': "Give options on the reconciliation propositions",
    'description': """
        Give options on the reconciliation propositions
        Merge from account_bank_reconciliation_rule module:
        A new rule is applied when doing bank reconciliation:
        -   if account_code of account.move.line = account_code of
        bank.statement.line  => the transaction is matched,
        -   if account_code of account.move.line != account_code
        of bank.statement.line => a new move is generated,
        move.line on source account is allocated and counterpart
        on bank journal account is matched to the statement.
    """,
    'author': 'La Louve, Druidoo',
    'website': 'http://www.lalouve.net',
    "license": "AGPL-3",
    'depends': [
        'account',
    ],
    'data': [
        "views/account_journal.xml",
    ],
    'installable': True,
}
