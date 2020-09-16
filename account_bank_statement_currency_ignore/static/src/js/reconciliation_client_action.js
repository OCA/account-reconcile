/**
 * Copyright 2020 CorporateHub (https://corporatehub.eu)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 */
odoo.define("account_bank_statement_currency_ignore.ReconciliationClientAction", function (require) {
    "use strict";

    var ReconciliationClientAction = require("account.ReconciliationClientAction");

    ReconciliationClientAction.StatementAction.include({
        custom_events: _.extend({}, ReconciliationClientAction.StatementAction.prototype.custom_events, {
            toggle_ignore_currency: "_onToggleIgnoreCurrency",
        }),
        _onToggleIgnoreCurrency: function (e) {
            console.log(e.data);
            // var self = this;
            // var handle = event.target.handle;
            // var line = this.model.getLine(handle);
            // var amount = this.model.getPartialReconcileAmount(handle, event.data);
            // self._getWidget(handle).updatePartialAmount(event.data.data, amount);

            // TODO: call and rerender

            // on Model,
            // /**
            //  * RPC method to load informations on lines
            //  *
            //  * @param {Array} ids ids of bank statement line passed to rpc call
            //  * @param {Array} excluded_ids list of move_line ids that needs to be excluded from search
            //  * @returns {Deferred}
            //  */
            // loadData: function(ids, excluded_ids) {
            //     var self = this;
            //     return self._rpc({
            //         model: 'account.reconciliation.widget',
            //         method: 'get_bank_statement_line_data',
            //         args: [ids, excluded_ids],
            //         context: self.context,
            //     })
            //     .then(function(res){
            //         return self._formatLine(res['lines']);
            //     })
            // },

            // also see on Action:
            // /**
            //  *
            //  */
            // _loadMore: function(qty) {
            //     var self = this;
            //     return this.model.loadMore(qty).then(function () {
            //         self._renderLines();
            //     });
            // },
        },
    });
});
