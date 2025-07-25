/* global CustomEvent */
import {formatDate, parseDate} from "@web/core/l10n/dates";
import {getCurrency} from "@web/core/currency";
import {floatIsZero} from "@web/core/utils/numbers";
import {formatMonetary} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const {Component} = owl;

export class AccountReconcileDataWidget extends Component {
    static props = {
        ...standardFieldProps,
    };
    static template = "account_reconcile_oca.ReconcileDataWidget";
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.action = useService("action");
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
        const totals = {debit: 0, credit: 0};
        if (!data || !data.length) {
            return {lines: [], totals};
        }
        for (var line in data) {
            data[line].amount_format = formatMonetary(data[line].amount, {
                currencyId: data[line].currency_id,
            });
            data[line].debit_format = formatMonetary(data[line].debit, {
                currencyId: data[line].currency_id,
            });
            data[line].credit_format = formatMonetary(data[line].credit, {
                currencyId: data[line].currency_id,
            });
            data[line].amount_currency_format = formatMonetary(
                data[line].currency_amount,
                {
                    currencyId: data[line].line_currency_id,
                }
            );
            if (data[line].original_amount) {
                data[line].original_amount_format = formatMonetary(
                    data[line].original_amount,
                    {
                        currencyId: data[line].currency_id,
                    }
                );
            }
            data[line].date_format = formatDate(
                parseDate(data[line].date, undefined, {isUTC: true})
            );
            totals.debit += data[line].debit || 0;
            totals.credit += data[line].credit || 0;
        }
        totals.balance = totals.debit - totals.credit;
        const [firstLine = {}] = Object.values(data);
        const currency = getCurrency(firstLine.currency_id);
        const decimals = currency.digits[1];
        const hasOpenBalance = !floatIsZero(totals.balance, decimals);
        const absoluteBalance = Math.abs(totals.balance);
        const openDebitFmt =
            totals.balance < 0 ? formatMonetary(absoluteBalance, {currency}) : null;
        const openCreditFmt =
            totals.balance > 0 ? formatMonetary(absoluteBalance, {currency}) : null;
        return {lines: data, hasOpenBalance, openDebitFmt, openCreditFmt};
    }
    onTrashLine(ev, line) {
        ev.stopPropagation();
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
    async openMove(ev, moveId) {
        ev.preventDefault();
        ev.stopPropagation();
        // eslint-disable-next-line no-undef
        console.log(moveId);
        const action = await this.orm.call("account.move", "get_formview_action", [
            [moveId],
        ]);
        this.action.doAction(action);
    }
}

export const AccountReconcileDataWidgetField = {
    component: AccountReconcileDataWidget,
    supportedTypes: [],
};
registry
    .category("fields")
    .add("account_reconcile_oca_data", AccountReconcileDataWidgetField);
