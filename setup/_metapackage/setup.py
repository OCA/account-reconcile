import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_bank_statement_reopen_skip_undo_reconciliation>=15.0dev,<15.1dev',
        'odoo-addon-account_mass_reconcile>=15.0dev,<15.1dev',
        'odoo-addon-account_mass_reconcile_by_purchase_line>=15.0dev,<15.1dev',
        'odoo-addon-account_move_reconcile_forbid_cancel>=15.0dev,<15.1dev',
        'odoo-addon-account_move_reconcile_helper>=15.0dev,<15.1dev',
        'odoo-addon-account_partner_reconcile>=15.0dev,<15.1dev',
        'odoo-addon-account_reconcile_payment_order>=15.0dev,<15.1dev',
        'odoo-addon-account_reconcile_restrict_partner_mismatch>=15.0dev,<15.1dev',
        'odoo-addon-account_reconciliation_widget>=15.0dev,<15.1dev',
        'odoo-addon-account_reconciliation_widget_due_date>=15.0dev,<15.1dev',
        'odoo-addon-account_reconciliation_widget_limit_aml>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
