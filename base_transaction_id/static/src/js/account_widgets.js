odoo.define('base_transaction_id.base_transaction_id', function (require) {

    var AccountReconciliation = require('account.reconciliation');

    AccountReconciliation.bankStatementReconciliation.include({
        decorateMoveLine: function(line) {
            this._super(line);
            if (line.transaction_ref) {
                line.q_label += ' (' + line.transaction_ref + ')';
            }
        },
    });

});
