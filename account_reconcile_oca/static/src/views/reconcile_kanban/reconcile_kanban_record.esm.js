import {KanbanRecord, kanbanRecordProps} from "@web/views/kanban/kanban_record";
import {t, useProps} from "@odoo/owl";

export class ReconcileKanbanRecord extends KanbanRecord {
    props = useProps({
        ...kanbanRecordProps,
        selectedRecordId: t.any().optional(),
    });
    getCardClasses() {
        var result = super.getCardClasses();
        if (this.props.selectedRecordId === this.props.record.resId) {
            result += " o_kanban_record_reconcile_oca_selected";
        }
        return result;
    }
}
