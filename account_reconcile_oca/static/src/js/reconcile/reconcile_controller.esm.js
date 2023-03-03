/** @odoo-module */
const {useState, useSubEnv} = owl;
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {View} from "@web/views/view";
import {useService} from "@web/core/utils/hooks";

export class ReconcileController extends KanbanController {
    async setup() {
        super.setup();
        this.state = useState({
            selectedRecordId: null,
        });
        useSubEnv({
            parentController: this,
            exposeController: this.exposeController.bind(this),
        });
        this.effect = useService("effect");
        this.orm = useService("orm");
        this.action = useService("action");
        this.router = useService("router");
        this.activeActions = this.props.archInfo.activeActions;
        this.model.addEventListener("update", () => this.selectRecord(), {once: true});
    }
    exposeController(controller) {
        this.form_controller = controller;
    }
    async onClickNewButton() {
        const action = await this.orm.call(this.props.resModel, "action_new_line", [], {
            context: this.props.context,
        });
        this.action.doAction(action, {
            onClose: async () => {
                await this.model.root.load();
                this.render(true);
            },
        });
    }
    async setRainbowMan(message) {
        this.effect.add({
            message,
            type: "rainbow_man",
        });
    }
    get viewReconcileInfo() {
        return {
            resId: this.state.selectedRecordId,
            type: "form",
            context: {
                ...(this.props.context || {}),
                form_view_ref: this.props.context.view_ref,
            },
            display: {controlPanel: false},
            mode: this.props.mode || "edit",
            resModel: this.props.resModel,
        };
    }
    async selectRecord(record) {
        var resId = undefined;
        if (record === undefined && this.props.resId) {
            resId = this.props.resId;
        } else if (record === undefined) {
            var records = this.model.root.records.filter(
                (modelRecord) =>
                    !modelRecord.data.is_reconciled || modelRecord.data.to_check
            );
            if (records.length === 0) {
                records = this.model.root.records;
                if (records.length === 0) {
                    this.state.selectedRecordId = false;
                    return;
                }
            }
            resId = records[0].resId;
        } else {
            resId = record.resId;
        }
        if (this.state.selectedRecordId && this.state.selectedRecordId !== resId) {
            if (this.form_controller.model.root.isDirty) {
                await this.form_controller.model.root.save({
                    noReload: true,
                    stayInEdition: true,
                    useSaveErrorDialog: true,
                });
                await this.model.root.load();
                await this.render(true);
            }
        }
        if (!this.state.selectedRecordId || this.state.selectedRecordId !== resId) {
            this.state.selectedRecordId = resId;
        }
        this.updateURL(resId);
    }
    async openRecord(record) {
        this.selectRecord(record);
    }
    updateURL(resId) {
        this.router.pushState({id: resId});
    }
}
ReconcileController.components = {
    ...ReconcileController.components,
    View,
};

ReconcileController.template = "account_reconcile_oca.ReconcileController";
ReconcileController.defaultProps = {};
