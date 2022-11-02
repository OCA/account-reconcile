/* Copyright 2021 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define(
    "account_reconciliation_widget_due_date.ReconciliationClientAction",
    function (require) {
        "use strict";

        const ReconciliationClientAction = require("account.ReconciliationClientAction");

        ReconciliationClientAction.StatementAction.include({
            custom_events: _.extend(
                {},
                ReconciliationClientAction.StatementAction.prototype.custom_events,
                {
                    change_date_due: "_onAction",
                }
            ),
        });
    }
);
