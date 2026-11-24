import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {ReconcileMoveLineKanbanRecord} from "./reconcile_move_line_kanban_record.esm.js";

export class ReconcileMoveLineKanbanRenderer extends KanbanRenderer {
    /**
     * Same check as ReconcileMoveLineRenderer.getRowClass. It is evaluated here,
     * while rendering the renderer, so the cards are refreshed whenever the
     * counterparts of the parent record change.
     */
    isCounterpart(record) {
        const info = this.props.parentRecord.data.reconcile_data_info;
        return Boolean(info && info.counterparts.includes(record.resId));
    }
    toggleSelection() {
        // Same as allowSelectors=false on the list: no multi-selection
        // (alt+click, long touch), a click always selects a counterpart.
    }
}
ReconcileMoveLineKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: ReconcileMoveLineKanbanRecord,
};
ReconcileMoveLineKanbanRenderer.template =
    "account_reconcile_oca.ReconcileMoveLineKanbanRenderer";
ReconcileMoveLineKanbanRenderer.props = [
    ...KanbanRenderer.props,
    "parentRecord",
    "parentField",
];
