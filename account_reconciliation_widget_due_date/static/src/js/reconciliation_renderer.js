odoo.define("account_reconciliation_widget_due_date.ReconciliationRenderer", function(
    require
) {
    "use strict";

    var renderer = require("account.ReconciliationRenderer");
    var basic_fields = require("web.basic_fields");
    var core = require("web.core");
    var _t = core._t;

    renderer.LineRenderer.include({
        _onFieldChanged: function(event) {
            var fieldName = event.target.name;
            if (fieldName === "date_due") {
                var date_due = event.data.changes.date_due;
                this.trigger_up("change_date_due", {data: date_due});
            } else {
                this._super.apply(this, arguments);
            }
        },
        start: function() {
            this._super.apply(this, arguments);
            var self = this;
            this._makeDateDueRecord().then(function(recordID) {
                self.fields.date_due = new basic_fields.FieldDate(
                    self,
                    "date_due",
                    self.model.get(recordID),
                    {
                        mode: "edit",
                        attrs: {placeholder: _t("Select Due date")},
                    }
                );
                if (self._initialState.st_line.date_due !== "") {
                    self.fields.date_due.value = self._initialState.st_line.date_due;
                }
                self.fields.date_due.insertAfter(
                    self.$(".accounting_view caption .o_buttons")
                );
            });
        },
        _makeDateDueRecord: function() {
            var field = {
                type: "date",
                name: "date_due",
            };
            return this.model.makeRecord("account.bank.statement.line", [field], {
                date_due: {},
            });
        },
    });
});
