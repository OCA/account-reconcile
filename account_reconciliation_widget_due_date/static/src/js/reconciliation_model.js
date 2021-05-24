/* eslint-disable init-declarations */
/* eslint-disable-line no-shadow */
odoo.define("account_reconciliation_widget_due_date.ReconciliationModel", function(
    require
) {
    "use strict";

    var Model = require("account.ReconciliationModel");
    var utils = require("web.utils");
    var session = require("web.session");
    var core = require("web.core");
    var _t = core._t;
    Model.StatementModel.include({
        changeDateDue: function(handle, date_due, preserveMode) {
            var self = this;
            var line = this.getLine(handle);
            line.st_line.date_due = date_due;
            return Promise.resolve(date_due)
                .then(function() {
                    return self._computeLine(line);
                })
                .then(function() {
                    return self.changeMode(
                        handle,
                        preserveMode ? line.mode : "default",
                        true
                    );
                });
        },
        validate: function(handle) {
            var self = this;
            this.display_context = "validate";
            var handles = [];
            if (handle) {
                handles = [handle];
            } else {
                _.each(this.lines, function(line, handle) {
                    if (
                        !line.reconciled &&
                        line.balance &&
                        !line.balance.amount &&
                        line.reconciliation_proposition.length
                    ) {
                        handles.push(handle);
                    }
                });
            }
            var ids = [];
            var values = [];
            var handlesPromises = [];
            _.each(handles, function(handle) {
                var line = self.getLine(handle);
                var props = _.filter(line.reconciliation_proposition, function(prop) {
                    return !prop.invalid;
                });
                var computeLinePromise;
                if (props.length === 0) {
                    // Usability: if user has not chosen any lines and click validate, it has the same behavior
                    // as creating a write-off of the same amount.
                    props.push(
                        self._formatQuickCreate(line, {
                            account_id: [
                                line.st_line.open_balance_account_id,
                                self.accounts[line.st_line.open_balance_account_id],
                            ],
                        })
                    );
                    // Update balance of line otherwise it won't be to zero and another line will be added
                    line.reconciliation_proposition.push(props[0]);
                    computeLinePromise = self._computeLine(line);
                }
                ids.push(line.id);
                handlesPromises.push(
                    Promise.resolve(computeLinePromise).then(function() {
                        var values_dict = {
                            partner_id: line.st_line.partner_id,
                            counterpart_aml_dicts: _.map(
                                _.filter(props, function(prop) {
                                    return !isNaN(prop.id) && !prop.already_paid;
                                }),
                                self._formatToProcessReconciliation.bind(self, line)
                            ),
                            payment_aml_ids: _.pluck(
                                _.filter(props, function(prop) {
                                    return !isNaN(prop.id) && prop.already_paid;
                                }),
                                "id"
                            ),
                            new_aml_dicts: _.map(
                                _.filter(props, function(prop) {
                                    return isNaN(prop.id) && prop.display;
                                }),
                                self._formatToProcessReconciliation.bind(self, line)
                            ),
                            to_check: line.to_check,
                            date_due: line.st_line.date_due,
                        };

                        // If the lines are not fully balanced, create an unreconciled amount.
                        // line.st_line.currency_id is never false here because its equivalent to
                        // statement_line.currency_id or statement_line.journal_id.currency_id or statement_line.journal_id.company_id.currency_id (Python-side).
                        // see: get_statement_line_for_reconciliation_widget method in account/models/account_bank_statement.py for more details
                        var currency = session.get_currency(line.st_line.currency_id);
                        var balance = line.balance.amount;
                        if (!utils.float_is_zero(balance, currency.digits[1])) {
                            var unreconciled_amount_dict = {
                                account_id: line.st_line.open_balance_account_id,
                                credit: balance > 0 ? balance : 0,
                                debit: balance < 0 ? -balance : 0,
                                name: line.st_line.name + " : " + _t("Open balance"),
                            };
                            values_dict.new_aml_dicts.push(unreconciled_amount_dict);
                        }
                        values.push(values_dict);
                        line.reconciled = true;
                    })
                );

                _.each(self.lines, function(other_line) {
                    if (other_line != line) {
                        var filtered_prop = other_line.reconciliation_proposition.filter(
                            p =>
                                !line.reconciliation_proposition
                                    .map(l => l.id)
                                    .includes(p.id)
                        );
                        if (
                            filtered_prop.length !=
                            other_line.reconciliation_proposition.length
                        ) {
                            other_line.need_update = true;
                            other_line.reconciliation_proposition = filtered_prop;
                        }
                        self._computeLine(line);
                    }
                });
            });

            return Promise.all(handlesPromises).then(function() {
                return self
                    ._rpc({
                        model: "account.reconciliation.widget",
                        method: "process_bank_statement_line",
                        args: [ids, values],
                        context: self.context,
                    })
                    .then(self._validatePostProcess.bind(self))
                    .then(function() {
                        self.valuenow += handles.length;
                        return {handles: handles};
                    });
            });
        },
    });
});
