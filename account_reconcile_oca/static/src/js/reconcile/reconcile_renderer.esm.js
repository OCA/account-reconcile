/** @odoo-module */

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {ReconcileKanbanRecord} from "./reconcile_kanban_record.esm.js";
export class ReconcileRenderer extends KanbanRenderer {
    get journalBalanceStr() {
        console.log(this);
    }
}

ReconcileRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: ReconcileKanbanRecord,
};
ReconcileRenderer.template = "account_reconcile_oca.ReconcileRenderer";
ReconcileRenderer.props = [...KanbanRenderer.props, "selectedRecordId?"];
