import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_mass_reconcile',
        'odoo13-addon-account_partner_reconcile',
        'odoo13-addon-account_reconcile_payment_order',
        'odoo13-addon-account_reconcile_restrict_partner_mismatch',
        'odoo13-addon-account_skip_bank_reconciliation',
        'odoo13-addon-bank_statement_journal_items',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
