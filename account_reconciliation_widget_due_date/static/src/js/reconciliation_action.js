odoo.define(
    "account_reconciliation_widget_due_date.ReconciliationClientAction",
    function(require) {
        "use strict";
        var action = require("account.ReconciliationClientAction");

        action.StatementAction.include({
            custom_events: _.extend(
                {},
                action.StatementAction.prototype.custom_events,
                {
                    change_date_due: "_onAction",
                }
            ),
        });
    }
);
