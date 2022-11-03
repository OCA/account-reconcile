/* Copyright 2021 Tecnativa - Víctor Martínez
 * Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define(
    "account_reconciliation_widget_due_date.ReconciliationModel",
    function (require) {
        "use strict";

        const ReconciliationModel = require("account.ReconciliationModel");

        ReconciliationModel.StatementModel.include({
            /**
             * @param {String} handle
             * @param {Moment} date_due
             * @param {Boolean} preserveMode
             * @returns {Promise}
             */
            changeDateDue: function (handle, date_due, preserveMode) {
                const line = this.getLine(handle);
                line.st_line.date_due = date_due;

                return this._computeLine(line)
                    .then(() =>
                        this.changeMode(
                            handle,
                            preserveMode ? line.mode : "default",
                            true
                        )
                    )
                    .then(() => date_due);
            },

            /**
             * @override
             */
            _validatePostProcess: function (data) {
                if (_.isEmpty(this._validateLineHandles)) {
                    return this._super.apply(this, arguments);
                }
                const line_ids = [];
                const dates = [];
                for (const handle of this._validateLineHandles) {
                    const line = this.getLine(handle);
                    line_ids.push(line.id);
                    dates.push(line.st_line.date_due);
                }

                const tasks = [];
                tasks.push(this._super.apply(this, arguments));
                tasks.push(
                    this._rpc({
                        model: "account.reconciliation.widget",
                        method: "update_bank_statement_line_due_date",
                        args: [data.moves, line_ids, dates],
                        context: this.context,
                    })
                );
                return Promise.all(tasks);
            },

            /**
             * @override
             */
            validate: function (handle) {
                // TODO: Check if need recalculate this is next versions
                let line_handles = [];
                if (handle) {
                    line_handles = [handle];
                } else {
                    _.each(this.lines, (line, line_handle) => {
                        if (
                            !line.reconciled &&
                            line.balance &&
                            !line.balance.amount &&
                            line.reconciliation_proposition.length
                        ) {
                            line_handles.push(line_handle);
                        }
                    });
                }

                // HACK: Store handles to use it in '_validatePostProcess' and frees at promise resolution
                this._validateLineHandles = line_handles;
                return this._super.apply(this, arguments).then((results) => {
                    this._validateLineHandles = null;
                    return results;
                });
            },
        });
    }
);
