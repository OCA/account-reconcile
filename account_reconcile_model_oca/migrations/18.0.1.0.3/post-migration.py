from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    reconciliation_model_lines = env["account.reconcile.model.line"].search(
        [("amount_type", "=", "percentage_st_line")]
    )
    env.add_to_compute(
        reconciliation_model_lines._fields["amount_type"], reconciliation_model_lines
    )
