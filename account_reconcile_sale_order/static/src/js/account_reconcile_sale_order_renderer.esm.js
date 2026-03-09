/** @odoo-module */

import {ListRenderer} from "@web/views/list/list_renderer";

export class ReconcileSaleOrderRenderer extends ListRenderer {
    getRowClass(record) {
        var classes = super.getRowClass(record);
        if (
            this.props.parentRecord.data.reconcile_data_info.data.find(
                (line) => line.sale_order_id === record.resId
            )
        ) {
            classes += " o_field_account_reconcile_oca_move_line_selected table-info";
        }
        return classes;
    }
}
ReconcileSaleOrderRenderer.props = [
    ...ListRenderer.props,
    "parentRecord",
    "parentField",
];
