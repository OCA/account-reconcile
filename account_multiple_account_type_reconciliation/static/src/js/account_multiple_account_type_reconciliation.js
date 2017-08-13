//-*- coding: utf-8 -*-
//© 2017 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.account_multiple_account_type_reconciliation = function(instance) {
	instance.web.account.bankStatementReconciliationLine.include({

		selectMoveLine : function(mv_line) {
			var self = this;
			var line_id = mv_line.dataset.lineid;

			// find the line in mv_lines or mv_lines_deselected
			var line = _.find(self.get("mv_lines"), function(o) {
				return o.id == line_id
			});
			if (!line) {
				line = _.find(self.mv_lines_deselected, function(o) {
					return o.id == line_id
				});
				self.mv_lines_deselected = _.filter(self.mv_lines_deselected,
						function(o) {
							return o.id != line_id
						});
			}
			if (!line)
				return; // If no line found, we've got a syncing problem (let's
						// turn a deaf ear)
			self.set("mv_lines_selected", self.get("mv_lines_selected").concat(
					line));
		}
	});
};
