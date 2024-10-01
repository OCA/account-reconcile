# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    cr.execute(
        """
        INSERT INTO account_payment_order_maturity (
            payment_order_id,
            date,
            currency_id,
            company_id,
            payment_type,
            is_matched
        )
        SELECT
            apo.id,
            apl.date,
            ap.currency_id,
            apo.company_id,
            apo.payment_type,
            bool_and(ap.is_matched)
        FROM
            account_payment_order apo
            INNER JOIN account_payment ap
                ON ap.payment_order_id = apo.id
            INNER JOIN account_payment_account_payment_line_rel apaplr
                ON apaplr.account_payment_id = ap.id
            INNER JOIN account_payment_line apl
                ON apl.id = apaplr.account_payment_line_id
            INNER JOIN account_move_line aml
                ON aml.move_id = ap.move_id
            INNER JOIN account_account aa
                ON aa.id = aml.account_id
        WHERE apo.state = 'uploaded'
        GROUP BY apo.id, apl.date, ap.currency_id
    """
    )
    cr.execute(
        """
        UPDATE account_payment ap
        SET maturity_order_id = apom.id
        FROM account_payment_order_maturity apom
        INNER JOIN account_payment_line apl
            ON apl.order_id = apom.payment_order_id
        INNER JOIN account_payment_account_payment_line_rel apaplr
            ON apl.id = apaplr.account_payment_line_id
        WHERE
            apaplr.account_payment_id = ap.id
            AND apom.date = apl.date
            AND apom.currency_id = ap.currency_id
    """
    )
    env = api.Environment(cr, SUPERUSER_ID, {})

    # We assume that there will not be too many records to process
    env["account.payment.order.maturity"].search(
        [("is_matched", "=", False)]
    )._compute_matched_info()
