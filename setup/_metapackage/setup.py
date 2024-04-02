import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_mass_reconcile>=16.0dev,<16.1dev',
        'odoo-addon-account_move_base_import>=16.0dev,<16.1dev',
        'odoo-addon-account_move_line_reconcile_manual>=16.0dev,<16.1dev',
        'odoo-addon-account_move_reconcile_forbid_cancel>=16.0dev,<16.1dev',
        'odoo-addon-account_move_so_import>=16.0dev,<16.1dev',
        'odoo-addon-account_reconcile_oca>=16.0dev,<16.1dev',
        'odoo-addon-account_statement_base>=16.0dev,<16.1dev',
        'odoo-addon-base_transaction_id>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
