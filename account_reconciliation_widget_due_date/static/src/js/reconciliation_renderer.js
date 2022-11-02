/* Copyright 2021 Tecnativa - Víctor Martínez
 * Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define(
    "account_reconciliation_widget_due_date.ReconciliationRenderer",
    function (require) {
        "use strict";

        const ReconciliationRenderer = require("account.ReconciliationRenderer");
        const basic_fields = require("web.basic_fields");
        const core = require("web.core");

        const _t = core._t;

        ReconciliationRenderer.LineRenderer.include({
            /**
             * @override
             */
            _onFieldChanged: function (event) {
                const fieldName = event.target.name;
                if (fieldName === "date_due") {
                    const date_due = event.data.changes.date_due;
                    this.trigger_up("change_date_due", {data: date_due});
                } else {
                    this._super.apply(this, arguments);
                }
            },

            /**
             * @override
             */
            start: function () {
                return Promise.all([
                    this._super.apply(this, arguments),
                    this._makeDateDueRecord(),
                ]);
            },

            /**
             *
             * @returns {Promise}
             */
            _makeDateDueRecord: function () {
                const field = {
                    type: "date",
                    name: "date_due",
                };
                return this.model
                    .makeRecord("account.bank.statement.line", [field], {
                        date_due: {},
                    })
                    .then((recordID) => {
                        this.fields.date_due = new basic_fields.FieldDate(
                            this,
                            "date_due",
                            this.model.get(recordID),
                            {
                                mode: "edit",
                                attrs: {placeholder: _t("Select Due date")},
                            }
                        );
                        if (this._initialState.st_line.date_due !== "") {
                            this.fields.date_due.value =
                                this._initialState.st_line.date_due;
                        }
                        this.fields.date_due.appendTo(
                            this.$(".accounting_view caption")
                        );
                    });
            },
        });
    }
);
