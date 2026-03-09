/** @odoo-module */

import {ListController} from "@web/views/list/list_controller";

export class ReconcileSaleOrderController extends ListController {
    async openRecord(record) {
        var data = {};
        data[this.props.parentField] = [record.resId, record.display_name];
        this.props.parentRecord.update(data);
    }
}

ReconcileSaleOrderController.template =
    "account_reconcile_sale_order.ReconcileSaleOrderController";
ReconcileSaleOrderController.props = {
    ...ListController.props,
    parentRecord: {type: Object, optional: true},
    parentField: {type: String, optional: true},
};
