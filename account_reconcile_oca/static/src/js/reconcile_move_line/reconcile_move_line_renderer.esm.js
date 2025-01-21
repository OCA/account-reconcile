import {ListRenderer} from "@web/views/list/list_renderer";

export class ReconcileMoveLineRenderer extends ListRenderer {
    getRowClass(record) {
        var classes = super.getRowClass(record);
        if (
            this.props.parentRecord.data.reconcile_data_info.counterparts.includes(
                record.resId
            )
        ) {
            classes += " o_field_account_reconcile_oca_move_line_selected table-info";
        }
        return classes;
    }
}
ReconcileMoveLineRenderer.props = [
    ...ListRenderer.props,
    "parentRecord",
    "parentField",
];
