/**
 * Copyright 2020 CorporateHub (https://corporatehub.eu)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 */
odoo.define("account_bank_statement_currency_ignore.ReconciliationRenderer", function (require) {
    "use strict";

    var ReconciliationRenderer = require("account.ReconciliationRenderer");

    ReconciliationRenderer.LineRenderer.include({
        events: _.extend({}, ReconciliationRenderer.LineRenderer.prototype.events, {
            "click .accounting_view .toggle_ignore_currency": "_onToggleIgnoreCurrency",
        }),
        _onToggleIgnoreCurrency: function (e) {
            e.stopPropagation();
            var lineId = $(e.target).closest(".o_reconciliation_line").data("line-id");
            this.trigger_up("toggle_ignore_currency", {"data": lineId});
        },
        //     updatePartialAmount: function(line_id, amount) {
        //         var $line = this.$(".mv_line[data-line-id="+line_id+"]");
        //         $line.find(".line_info_edit").addClass("o_hidden");
        //         $line.find(".edit_amount_input").removeClass("o_hidden");
        //         $line.find(".edit_amount_input").focus();
        //         $line.find(".edit_amount_input").val(amount.toFixed(2));
        //         $line.find(".edit_amount_input").select();
        //         $line.find(".line_amount").addClass("o_hidden");
        //     },
        //     _editAmount: function (event) {
        //         event.stopPropagation();
        //         var $line = $(event.target);
        //         var moveLineId = $line.closest(".mv_line").data("line-id");
        //         this.trigger_up(
        //             "partial_reconcile",
        //             {"data": {mvLineId: moveLineId, "amount": $line.val()}}
        //         );
        //     },
        //     _onInputKeyup: function (event) {
        //         if(event.keyCode === 13) {
        //             if ($(event.target).hasClass("edit_amount_input")) {
        //                 $(event.target).blur();
        //                 return;
        //             }
        //         }
        //         if ($(event.target).hasClass("edit_amount_input")) {
        //             if (event.type === "keyup") {
        //                 return;
        //             }
        //             else {
        //                 return this._editAmount(event);
        //             }
        //         }
        //         return this._super.apply(this, arguments);
        //     },
    });
});
