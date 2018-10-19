import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_mass_reconcile',
        'odoo11-addon-account_mass_reconcile_by_purchase_line',
        'odoo11-addon-account_mass_reconcile_transaction_ref',
        'odoo11-addon-bank_statement_foreign_currency',
        'odoo11-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
