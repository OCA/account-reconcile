# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    cr.execute("""
        ALTER TABLE account_bank_statement_line
            ADD original_amount_currency numeric;
        COMMENT
            ON COLUMN account_bank_statement_line.original_amount_currency
            IS 'Original Amount Currency';
        ALTER TABLE account_bank_statement_line
            ADD original_currency_id integer
            CONSTRAINT account_bank_statement_line_original_currency_id_fkey
                REFERENCES res_currency
                    ON DELETE SET NULL;
        COMMENT
            ON COLUMN account_bank_statement_line.original_currency_id
            IS 'Original Currency';
        UPDATE account_bank_statement_line
            SET
                original_amount_currency = amount_currency,
                original_currency_id = currency_id;
    """)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    statement_lines = env["account.bank.statement.line"].search([])
    statement_lines._compute_currency_id()
    statement_lines._compute_amount_currency()
