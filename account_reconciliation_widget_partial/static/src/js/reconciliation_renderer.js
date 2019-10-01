odoo.define('account_reconcile_partial.ReconciliationRenderer', function (require) {
    "use strict";

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
        updatePartialAmount: function(line_id, amount) {
            var $line = this.$('.mv_line[data-line-id='+line_id+']');
            $line.find('.line_info_edit').addClass('o_hidden');
            $line.find('.edit_amount_input').removeClass('o_hidden');
            $line.find('.edit_amount_input').focus();
            $line.find('.edit_amount_input').val(amount.toFixed(2));
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
    });
});
