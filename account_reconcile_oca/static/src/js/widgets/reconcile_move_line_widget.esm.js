/** @odoo-module **/

import {View} from "@web/views/view";
import {registry} from "@web/core/registry";
import {CallbackRecorder} from "@web/webclient/actions/action_hook";

const {Component, useSubEnv} = owl;

export class AccountReconcileMatchWidget extends Component {
    setup() {
        // Necessary in order to avoid a loop
        super.setup(...arguments);
        // Isolate this embedded View from the parent action's state
        // recorders by giving it its own local CallbackRecorders, the
        // same way action_service.js does for each ControllerComponent.
        // Without this, the inner WithSearch registers its searchModel
        // state on the parent action's __getGlobalState__ recorder. On
        // breadcrumb back, action_service merges every recorded
        // getGlobalState() under the same `searchModel` key (last write
        // wins), so the inner account.move.line searchModel state
        // overwrites the outer account.bank.statement.line one. The
        // outer kanban then restores with a domain referencing
        // account.move.line-only fields (e.g. `account_id.non_trade`
        // from the Trade Receivable/Payable filters of
        // `account_move_line_search_reconcile_view`) and crashes
        // `web_search_read` on `account.bank.statement.line`.
        useSubEnv({
            config: {},
            parentController: this.env.parentController,
            __beforeLeave__: new CallbackRecorder(),
            __getGlobalState__: new CallbackRecorder(),
            __getLocalState__: new CallbackRecorder(),
        });
    }
    get listViewProperties() {
        return {
            type: "list",
            display: {
                controlPanel: {
                    // Hiding the control panel buttons
                    "top-left": false,
                    "bottom-left": true,
                },
            },
            resModel: this.props.record.fields[this.props.name].relation,
            searchMenuTypes: ["filter"],
            domain: this.props.record.getFieldDomain(this.props.name).toList(),
            context: {
                ...this.props.record.getFieldContext(this.props.name),
            },
            // Disables de selector
            allowSelectors: false,
            // We need to force the search view in order to show the right one
            searchViewId: false,
            parentRecord: this.props.record,
            parentField: this.props.name,
            showButtons: false,
        };
    }
}
AccountReconcileMatchWidget.template = "account_reconcile_oca.ReconcileMatchWidget";

AccountReconcileMatchWidget.components = {
    ...AccountReconcileMatchWidget.components,
    View,
};

registry
    .category("fields")
    .add("account_reconcile_oca_match", AccountReconcileMatchWidget);
