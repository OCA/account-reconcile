/** @odoo-module */

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {ReconcileKanbanRecord} from "./reconcile_kanban_record.esm.js";
import {formatMonetary} from "@web/views/fields/formatters";

export class ReconcileRenderer extends KanbanRenderer {
    getStatements() {
        console.log(this.props);
        if (
            this.env.parentController.props.resModel !== "account.bank.statement.line"
        ) {
            return [];
        }
        const {list} = this.props;
        const statements = [];
        for (const record of list.records) {
            const statementId = record.data.statement_id && record.data.statement_id[0];
            if (
                statementId &&
                (!statements.length || statements[0].id !== statementId)
            ) {
                statements.push({
                    id: statementId,
                    name: record.data.statement_name,
                    balance: record.data.statement_balance_end_real,
                    balanceStr: formatMonetary(record.data.statement_balance_end_real, {
                        currencyId: record.data.currency_id[0],
                    }),
                });
            }
        }
        console.log(statements);
        return statements;
    }
}

ReconcileRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: ReconcileKanbanRecord,
};
ReconcileRenderer.template = "account_reconcile_oca.ReconcileRenderer";
ReconcileRenderer.props = [...KanbanRenderer.props, "selectedRecordId?"];
