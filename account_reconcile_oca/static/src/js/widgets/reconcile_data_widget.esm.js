/** @odoo-module **/

import fieldUtils from "web.field_utils";
import {registry} from "@web/core/registry";
import session from "web.session";

const {Component} = owl;

export class AccountReconcileDataWidget extends Component {
    setup() {
        super.setup(...arguments);
        this.foreignCurrency =
            this.props &&
            this.props.record &&
            (this.props.record.data.foreign_currency_id ||
                this.props.record.data.currency_id[0] !==
                    this.props.record.data.company_currency_id[0] ||
                this.props.record.data[this.props.name].data.some(
                    (item) => item.line_currency_id !== item.currency_id
                ));
    }
    getReconcileLines() {
        var data = this.props.record.data[this.props.name].data;
        for (var line in data) {
            data[line].amount_format = fieldUtils.format.monetary(
                data[line].amount,
                undefined,
                {
                    currency: session.get_currency(data[line].currency_id),
                }
            );
            data[line].debit_format = fieldUtils.format.monetary(
                data[line].debit,
                undefined,
                {
                    currency: session.get_currency(data[line].currency_id),
                }
            );
            data[line].credit_format = fieldUtils.format.monetary(
                data[line].credit,
                undefined,
                {
                    currency: session.get_currency(data[line].currency_id),
                }
            );
            data[line].amount_currency_format = fieldUtils.format.monetary(
                data[line].currency_amount,
                undefined,
                {
                    currency: session.get_currency(data[line].line_currency_id),
                }
            );
            if (data[line].original_amount) {
                data[line].original_amount_format = fieldUtils.format.monetary(
                    data[line].original_amount,
                    undefined,
                    {
                        currency: session.get_currency(data[line].currency_id),
                    }
                );
            }
            data[line].date_format = fieldUtils.format.date(
                fieldUtils.parse.date(data[line].date, undefined, {isUTC: true})
            );
        }
        return data;
    }
    onTrashLine(ev, line) {
        this.props.record.update({
            manual_reference: line.reference,
            manual_delete: true,
        });
    }
    selectReconcileLine(ev, line) {
        this.props.record.update({
            manual_reference: line.reference,
        });
        const triggerEv = new CustomEvent("reconcile-page-navigate", {
            detail: {
                name: "manual",
                originalEv: ev,
            },
        });
        this.env.bus.trigger("RECONCILE_PAGE_NAVIGATE", triggerEv);
    }
}
AccountReconcileDataWidget.template = "account_reconcile_oca.ReconcileDataWidget";

registry
    .category("fields")
    .add("account_reconcile_oca_data", AccountReconcileDataWidget);
