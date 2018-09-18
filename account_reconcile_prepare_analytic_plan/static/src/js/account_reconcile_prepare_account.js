//-*- coding: utf-8 -*-
//Copyright 2018 Therp BV <https://therp.nl>
//License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
openerp.account_reconcile_prepare_analytic_plan = function(instance) {
    instance.web.account.bankStatementReconciliationLine.include({
        initializeCreateForm: function() {
            var result = this._super.apply(this, arguments);
            this.analytics_id_field.set(
                'value', this.st_line.prepared_analytic_analytic_plan_id
            );
            return result;
        },
    });
}
