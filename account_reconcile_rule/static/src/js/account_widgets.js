odoo.define('account_reconcile_rule', function (require) {
    "use strict";

    var core = require('web.core');
    var reconciliation_renderer = require('account.ReconciliationRenderer');

    /**
    * Automatically apply reconciliation models according to the
    * reconciliation rules matching the current statement line and move
    * lines being reconciled.
    */
    reconciliation_renderer.LineRenderer.include({
        /**
        * Get the reconciliation models to apply through RPC call and
        * create the write off entries.
        */
        reconciliation_rule_models: function() {
            var self = this;
            // Get the statement line
            var line = this.model.getLine(this.handle);
            // Call the models_for_reconciliation through RPC
            this._rpc({
                model: 'account.reconcile.rule',
                method: 'models_for_reconciliation',
                args: [
                    line.st_line.id,
                    _.pluck(line.reconciliation_proposition, 'id')
                ],
            }).done(function(rule_models) {
                // Loop on each models and create the corresponding write off
                // entries
                _.each(rule_models, function (rule_model_id) {
                    self.trigger_up('quick_create_proposition',
                                    {'data': rule_model_id});
                });
            });
        },
        /*
        * Add the write off entries after the the line renderer is ready
        */
        start: function () {
            var self = this;
            var deferred = this._super();
            if (deferred) {
                deferred.done(this.reconciliation_rule_models());
            }
            return deferred;
        },
    });
});
