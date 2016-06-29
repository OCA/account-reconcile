odoo.define('account_operation_rule', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');

    var reconciliation = require('account.reconciliation');

    reconciliation.bankStatementReconciliationLine.include({
        init: function(parent, context) {
            this._super(parent, context);
            this.preset_auto_clicked = false;
        },

        operation_rules: function () {
            var self = this;
            var model_operation_rule = new Model("account.operation.rule");
            model_operation_rule.call("operations_for_reconciliation",
                [self.st_line.id, _.pluck(self.get("mv_lines_selected"), 'id')]
            ).then(function (operations) {
                _.each(operations, function (operation_id) {
                    var preset_btn = self.$("button.preset[data-presetid='" + operation_id + "']");
                    preset_btn.trigger('click');

                    // Cannot click on add_line link for user here
                    // even with a when().done()
                    // because preset_btn click handler makes a rpc call
                    // via formCreateInputChanged method
                    // and we have to wait for response
                    self.preset_auto_clicked = true;
                });
            });
        },

        /**
         * Click on add_line link if preset button have been clicked
         * automatically.
         */
        formCreateInputChanged: function(elt, val) {
            var self = this;
            var deferred = this._super(elt, val);
            deferred.done(function() {
                if (self.preset_auto_clicked) {
                    self.addLineBeingEdited();
                }
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
