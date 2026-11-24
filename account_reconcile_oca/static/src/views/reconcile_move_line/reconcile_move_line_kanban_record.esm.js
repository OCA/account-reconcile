import {KanbanRecord} from "@web/views/kanban/kanban_record";

export class ReconcileMoveLineKanbanRecord extends KanbanRecord {
    getRecordClasses() {
        let classes = super.getRecordClasses();
        if (this.props.isCounterpart) {
            classes += " o_field_account_reconcile_oca_move_line_selected";
        }
        return classes;
    }
}
ReconcileMoveLineKanbanRecord.props = [...KanbanRecord.props, "isCounterpart?"];
