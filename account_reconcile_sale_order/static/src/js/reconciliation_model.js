odoo.define("account_reconcile_sale_order.ReconciliationModel", function (require) {
    "use strict";
    var StatementModel = require("account.ReconciliationModel").StatementModel;

    StatementModel.include({
        _formatToProcessReconciliation: function (line, prop) {
            if (prop.sale_order_id) {
                return this._formatToProcessReconciliationSaleOrder(line, prop);
            }
            return this._super.apply(this, arguments);
        },
        _formatToProcessReconciliationSaleOrder: function (line, prop) {
            return {
                sale_order_id: prop.sale_order_id,
            };
        },
    });
});
