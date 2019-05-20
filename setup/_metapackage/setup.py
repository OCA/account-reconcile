import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-account_banking_reconciliation',
        'odoo10-addon-account_mass_reconcile',
        'odoo10-addon-account_mass_reconcile_by_purchase_line',
        'odoo10-addon-account_mass_reconcile_partner',
        'odoo10-addon-account_mass_reconcile_ref_deep_search',
        'odoo10-addon-account_mass_reconcile_transaction_ref',
        'odoo10-addon-account_move_base_import',
        'odoo10-addon-account_move_reconcile_helper',
        'odoo10-addon-account_set_reconcilable',
        'odoo10-addon-bank_statement_foreign_currency',
        'odoo10-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
