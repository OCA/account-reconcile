openerp.account_banking_partner_journal_account = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    
    instance.web.account.bankStatementReconciliationLine.include({
    
        /** Creating */
    
        initializeCreateForm: function() {
            var self = this;
    
            _.each(self.create_form, function(field) {
                field.set("value", false);
            });
            self.label_field.set("value", self.st_line.name);
            self.amount_field.set("value", -1*self.get("balance"));
            console.dir(self);
            self.account_id_field.set_value(self.st_line.account_id);
            self.account_id_field.focus();
        }
    
        
    });

};
