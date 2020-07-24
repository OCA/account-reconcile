import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_banking_reconciliation',
        'odoo12-addon-account_mass_reconcile',
        'odoo12-addon-account_mass_reconcile_ref_deep_search',
        'odoo12-addon-account_move_base_import',
        'odoo12-addon-account_move_reconcile_helper',
        'odoo12-addon-account_move_so_import',
        'odoo12-addon-account_move_transactionid_import',
        'odoo12-addon-account_partner_reconcile',
        'odoo12-addon-account_reconcile_payment_order',
        'odoo12-addon-account_reconcile_reconciliation_date',
        'odoo12-addon-account_reconcile_restrict_partner_mismatch',
        'odoo12-addon-account_reconcile_rule',
        'odoo12-addon-account_reconciliation_widget_partial',
        'odoo12-addon-account_set_reconcilable',
        'odoo12-addon-account_skip_bank_reconciliation',
        'odoo12-addon-bank_statement_foreign_currency',
        'odoo12-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
