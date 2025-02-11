/** @odoo-module */

import {ListController} from "@web/views/list/list_controller";

export class ReconcileMoveLineController extends ListController {
    async openRecord(record) {
        var data = {};
        data[this.props.parentField] = [record.resId, record.display_name];
        this.props.parentRecord.update(data);
    }
    async clickAddAll() {
        await this.props.parentRecord.save();
        await this.orm.call(this.props.parentRecord.resModel, "add_multiple_lines", [
            this.props.parentRecord.resIds,
            this.model.root.domain,
        ]);
        await this.props.parentRecord.load();
        this.props.parentRecord.model.notify();
    }
}

ReconcileMoveLineController.template = `account_reconcile_oca.ReconcileMoveLineController`;
ReconcileMoveLineController.props = {
    ...ListController.props,
    parentRecord: {type: Object, optional: true},
    parentField: {type: String, optional: true},
};
