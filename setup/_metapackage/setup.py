import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_mass_reconcile',
        'odoo9-addon-account_mass_reconcile_by_purchase_line',
        'odoo9-addon-account_mass_reconcile_ref_deep_search',
        'odoo9-addon-account_mass_reconcile_transaction_ref',
        'odoo9-addon-account_move_bankaccount_import',
        'odoo9-addon-account_move_base_import',
        'odoo9-addon-account_move_so_import',
        'odoo9-addon-account_move_transactionid_import',
        'odoo9-addon-account_operation_rule',
        'odoo9-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
