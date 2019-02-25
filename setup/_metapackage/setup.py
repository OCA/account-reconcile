import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
