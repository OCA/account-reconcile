import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_move_base_import',
        'odoo14-addon-account_partner_reconcile',
        'odoo14-addon-account_reconcile_reconciliation_date',
        'odoo14-addon-account_reconciliation_widget',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
