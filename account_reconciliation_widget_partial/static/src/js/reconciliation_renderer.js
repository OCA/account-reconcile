odoo.define('account_reconcile_partial.ReconciliationRenderer', function (require) {
    "use strict";

    var field_utils = require('web.field_utils');
    var renderer = require('account.ReconciliationRenderer')

    renderer.LineRenderer.include({
        events: _.extend({}, renderer.LineRenderer.prototype.events, {
            'click .accounting_view .line_info_edit.fa-pencil': '_onInfoEdit',
        }),
        _onInfoEdit: function(e){
            e.stopPropagation();
            var $line = $(event.target);
            this.trigger_up(
                'get_partial_amount',
                {'data': $line.closest('.mv_line').data('line-id')}
            );
        },
        updatePartialAmount: function(event, amount) {
            var line_id = event.data.data;
            var $line = this.$('.mv_line[data-line-id='+line_id+']');
            var handle = event.target.handle;
            var line = this.model.getLine(handle);
            var format_options = {
                currency_id: line.st_line.currency_id,
                noSymbol: true,
            };
            var amount = field_utils.format.monetary(
                    amount, {}, format_options);

            $line.find('.line_info_edit').addClass('o_hidden');
            $line.find('.edit_amount_input').removeClass('o_hidden');
            $line.find('.edit_amount_input').focus();
            $line.find('.edit_amount_input').val(amount);
            $line.find('.edit_amount_input').select();
            $line.find('.line_amount').addClass('o_hidden');
        },
        _editAmount: function (event) {
            event.stopPropagation();
            var $line = $(event.target);
            var moveLineId = $line.closest('.mv_line').data('line-id');
            this.trigger_up(
                'partial_reconcile',
                {'data': {mvLineId: moveLineId, 'amount': $line.val()}}
            );
        },
        _onInputKeyup: function (event) {
            if(event.keyCode === 13) {
                if ($(event.target).hasClass('edit_amount_input')) {
                    $(event.target).blur();
                    return;
                }
            }
            if ($(event.target).hasClass('edit_amount_input')) {
                if (event.type === 'keyup') {
                    return;
                }
                else {
                    return this._editAmount(event);
                }
            }
            return this._super.apply(this, arguments);
        },
        _onSelectProposition: function (event) {
            var $el = $(event.target);
            if ($el.hasClass('edit_amount_input')) {
                // When the input is clicked, it is not to select the line
                // but simply to write in the input field.
                // so there is no need to call super that usually removes the line
                return;
            }
            return this._super.apply(this, arguments);
        },
    });
});
