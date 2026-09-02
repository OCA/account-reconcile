const {onMounted, onWillStart, useState, useSubEnv} = owl;
import {useBus, useService} from "@web/core/utils/hooks";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {View} from "@web/views/view";
import {formatMonetary} from "@web/views/fields/formatters";
import {router} from "@web/core/browser/router";
import {useSetupAction} from "@web/search/action_hook";

export class ReconcileController extends KanbanController {
    async setup() {
        super.setup();
        this.initialLoad = true;
        this.selectedRecordIndex = -1;
        this.state = useState({
            selectedRecordId: this.props.state?.selectedRecordId,
            journalBalance: 0,
            currency: false,
        });
        useSetupAction({
            getLocalState: () => {
                return {
                    selectedRecordId: this.state.selectedRecordId,
                };
            },
        });
        useSubEnv({
            parentController: this,
            exposeController: this.exposeController.bind(this),
        });
        this.effect = useService("effect");
        this.orm = useService("orm");
        this.action = useService("action");
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
        } else if (
            this.initialLoad &&
            record === undefined &&
            this.state.selectedRecordId
        ) {
            resId = this.state.selectedRecordId;
        } else if (record === undefined) {
            var candidates = this.model.root.records.filter(
                (modelRecord) =>
                    !modelRecord.data.is_reconciled || modelRecord.data.to_check
            );
            if (candidates.length === 0) {
                candidates = this.model.root.records;
                if (candidates.length === 0) {
                    this.state.selectedRecordId = false;
                    this.selectedRecordIndex = -1;
                    return;
                }
            }
            resId = this.getRecordIdToSelect(candidates);
        } else {
            resId = record.resId;
        }
        this.initialLoad = false;
        if (this.state.selectedRecordId && this.state.selectedRecordId !== resId) {
            const formRecord = this.form_controller?.model?.root;
            if (formRecord && (await formRecord.isDirty())) {
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
        this.selectedRecordIndex = this.model.root.records.findIndex(
            (modelRecord) => modelRecord.resId === resId
        );
        this.updateURL(resId);
    }
    getRecordIdToSelect(candidates) {
        // When the selected record is no longer a candidate (usually because it
        // has just been reconciled), we select the next one instead of going
        // back to the first one of the list. If there is no next candidate, we
        // select the last one.
        const records = this.model.root.records;
        const previousId = this.state.selectedRecordId;
        var index = 0;
        if (previousId) {
            const previousIndex = records.findIndex(
                (modelRecord) => modelRecord.resId === previousId
            );
            if (previousIndex === -1) {
                // The record is not displayed anymore (e.g. the unreconciled
                // filter is set), so its former position is now held by the
                // record that followed it.
                index = this.selectedRecordIndex;
            } else if (candidates.some((candidate) => candidate.resId === previousId)) {
                return previousId;
            } else {
                index = previousIndex + 1;
            }
        }
        for (var i = Math.max(index, 0); i < records.length; i++) {
            if (candidates.includes(records[i])) {
                return records[i].resId;
            }
        }
        return candidates[candidates.length - 1].resId;
    }
    async openRecord(record) {
        this.selectRecord(record);
    }
    updateURL(resId) {
        router.pushState({id: resId});
    }
}

ReconcileController.components = {
    ...ReconcileController.components,
    View,
};

ReconcileController.template = "account_reconcile_oca.ReconcileController";
ReconcileController.defaultProps = {};
