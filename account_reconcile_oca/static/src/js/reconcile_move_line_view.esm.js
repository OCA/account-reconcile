/** @odoo-module */

import {ListController} from "@web/views/list/list_controller";
import {ListRenderer} from "@web/views/list/list_renderer";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export class ReconcileMoveLineRenderer extends ListRenderer {
    getRowClass(record) {
        var classes = super.getRowClass(record);
        if (
            this.props.parentRecord.data.reconcile_data_info.counterparts.includes(
                record.resId
            )
        ) {
            classes += " o_field_account_reconcile_oca_move_line_selected";
        }
        return classes;
    }
}
ReconcileMoveLineRenderer.props = [
    ...ListRenderer.props,
    "parentRecord",
    "parentField",
];
export class ReconcileMoveLineController extends ListController {
    async openRecord(record) {
        var data = {};
        data[this.props.parentField] = [record.resId, record.display_name];
        this.props.parentRecord.update(data);
    }
}

ReconcileMoveLineController.template = `account_reconcile_oca.ReconcileMoveLineController`;
ReconcileMoveLineController.props = {
    ...ListController.props,
    parentRecord: {type: Object, optional: true},
    parentField: {type: String, optional: true},
};
export const ReconcileMoveLineView = {
    ...listView,
    Controller: ReconcileMoveLineController,
    Renderer: ReconcileMoveLineRenderer,
};

registry.category("views").add("reconcile_move_line", ReconcileMoveLineView);
