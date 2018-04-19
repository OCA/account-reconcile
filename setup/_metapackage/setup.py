import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-account-reconcile",
    description="Meta package for oca-account-reconcile Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_advanced_reconcile',
        'odoo8-addon-account_bank_statement_period_from_line_date',
        'odoo8-addon-account_easy_reconcile',
        'odoo8-addon-account_invoice_reference',
        'odoo8-addon-account_reconcile_payment_order',
        'odoo8-addon-account_reconcile_prepare_account',
        'odoo8-addon-account_statement_operation_multicompany',
        'odoo8-addon-account_statement_operation_rule',
        'odoo8-addon-account_statement_operation_rule_dunning_fees',
        'odoo8-addon-base_transaction_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
