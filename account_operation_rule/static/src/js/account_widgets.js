odoo.define('account_operation_rule', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');

    var reconciliation = require('account.reconciliation');

    reconciliation.bankStatementReconciliationLine.include({
        operation_rules: function () {
            var self = this;
            var model_operation_rule = new Model("account.operation.rule");
            model_operation_rule.call("operations_for_reconciliation",
                [self.st_line.id,
                    _.pluck(self.get("mv_lines_selected"), 'id')])
                .then(function (operations) {
                    _.each(operations, function (operation_id) {
                        var preset_btn = self.$("button.preset[data-presetid='" + operation_id + "']");
                        preset_btn.click();
                        self.addLineBeingEdited();
                    });
                });
        },
        render: function () {
            var deferred = this._super();
            if (deferred) {
                deferred.done(this.operation_rules());
            }
            return deferred;
        },
        restart: function () {
            var deferred = this._super();
            deferred.done(this.operation_rules());
            return deferred;
        }
    });
});
