odoo.define("account_reconcile_partial.ReconciliationClientAction", function (require) {

    var action = require('account.ReconciliationClientAction');

    action.StatementAction.include({
        custom_events: _.extend({}, action.StatementAction.prototype.custom_events, {
            get_partial_amount: '_onActionPartialAmount',
            partial_reconcile: '_onAction',
        }),
        _onActionPartialAmount: function(event) {
            var self = this;
            var handle = event.target.handle;
            var line = this.model.getLine(handle);
            var amount = this.model.getPartialReconcileAmount(handle, event.data);
            self._getWidget(handle).updatePartialAmount(event.data.data, amount);
        },
    });
});
