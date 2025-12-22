import {ReconcileMoveLineController} from "@account_reconcile_oca/js/reconcile_move_line/reconcile_move_line_controller.esm";
import {ReconcileMoveLineRenderer} from "@account_reconcile_oca/js/reconcile_move_line/reconcile_move_line_renderer.esm";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export class ReconcileSaleOrderController extends ReconcileMoveLineController {}

export class ReconcileSaleOrderRenderer extends ReconcileMoveLineRenderer {
    getRowClass(record) {
        var classes = super
            .getRowClass(record)
            .replace(
                " o_field_account_reconcile_oca_move_line_selected table-info",
                ""
            );
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

export const ReconcileSaleOrderView = {
    ...listView,
    Controller: ReconcileSaleOrderController,
    Renderer: ReconcileSaleOrderRenderer,
    buttonTemplate: "reconcile_sale_order.ListView.Buttons",
};

registry.category("views").add("reconcile_sale_order", ReconcileSaleOrderView);
