/** @odoo-module */
const {onMounted, onWillStart, useState, useSubEnv} = owl;
import {useBus, useService} from "@web/core/utils/hooks";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {View} from "@web/views/view";
import {formatMonetary} from "@web/views/fields/formatters";

export class ReconcileController extends KanbanController {
    async setup() {
        super.setup();
        this.state = useState({
            selectedRecordId: null,
            journalBalance: 0,
            currency: false,
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
        useBus(this.model.bus, "update", () => {
            this.selectRecord();
        });
        onWillStart(() => {
            this.updateJournalInfo();
        });
        onMounted(() => {
            this.selectRecord();
        });
    }
    get journalId() {
        if (this.props.context.active_model === "account.journal") {
            return this.props.context.active_id;
        }
        return false;
    }
    async updateJournalInfo() {
        var journalId = this.journalId;
        if (!journalId) {
            return;
        }
        var result = await this.orm.call("account.journal", "read", [
            [journalId],
            ["current_statement_balance", "currency_id", "company_currency_id"],
        ]);
        this.state.journalBalance = result[0].current_statement_balance;
        this.state.currency = (result[0].currency_id ||
            result[0].company_currency_id)[0];
    }
    get journalBalanceStr() {
        if (!this.state.journalBalance) {
            return "";
        }
        return formatMonetary(this.state.journalBalance, {
            currencyId: this.state.currency,
        });
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
                await this.updateJournalInfo();
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
            noBreadcrumbs: true,
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
        var resId = false;
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
