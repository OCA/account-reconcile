import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_bank_statement_reopen_skip_undo_reconciliation',
        'odoo14-addon-account_mass_reconcile',
        'odoo14-addon-account_mass_reconcile_as_job',
        'odoo14-addon-account_mass_reconcile_by_mrp_production',
        'odoo14-addon-account_mass_reconcile_by_purchase_line',
        'odoo14-addon-account_mass_reconcile_by_sale_line',
        'odoo14-addon-account_mass_reconcile_ref_deep_search',
        'odoo14-addon-account_move_base_import',
        'odoo14-addon-account_move_line_reconcile_manual',
        'odoo14-addon-account_move_reconcile_helper',
        'odoo14-addon-account_partner_reconcile',
        'odoo14-addon-account_reconcile_model_strict_match_amount',
        'odoo14-addon-account_reconcile_payment_order',
        'odoo14-addon-account_reconcile_reconciliation_date',
        'odoo14-addon-account_reconcile_restrict_partner_mismatch',
        'odoo14-addon-account_reconciliation_widget',
        'odoo14-addon-account_reconciliation_widget_limit_aml',
        'odoo14-addon-bank_statement_check_number',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
