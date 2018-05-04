openerp.account_statement_partner_lines = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliationLine.include({
        
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.events["click .display_partner_move_line"] = "displayPartnerMoveLine";
        },
        
        displayPartnerMoveLine: function() {
            var self = this;
            this.pop = new instance.web.form.SelectCreatePopup(this);
            var domain = [['partner_id', '=', self.partner_id]];
            this.pop.select_element(
                'account.move.line', {
                    title: "",
                    readonly: true,
                    disable_multiple_selection: false,
                    no_create: true,
                }, domain, {});
            this.pop.on("elements_selected", self, function(element_ids) {
                new instance.web.Model("account.move.line").call("prepare_aml_for_reconciliation_from_ids", [element_ids, self.st_line.currency_id]).then(function(result) {
                    var mv_lines = [];
                    var mv_line_ids = []
                    _.each(result, function(line) {
                        self.decorateMoveLine(line, self.st_line.currency_id);
                        mv_lines.push(line);
                        mv_line_ids.push(line.id)
                    }, self);
                    self.set("mv_lines_selected", self.get("mv_lines_selected").concat(mv_lines));
                    self.mv_lines_deselected = _.filter(self.mv_lines_deselected, function(el){ return mv_line_ids.indexOf(el.id) === -1 });
                    self.updateMatches();
                });
            });

        }
    });
};