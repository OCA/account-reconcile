openerp.base_transaction_id = function (instance) {

    instance.web.account.bankStatementReconciliationLine.include({
        decorateMoveLine: function(line, currency_id) {
            this._super(line, currency_id);
            if (line.transaction_ref) {
                line.q_label += ' (' + line.transaction_ref + ')';
            }
        },
    });
};
