/** @odoo-module **/

import {View} from "@web/views/view";
import {registry} from "@web/core/registry";

const {Component, useSubEnv} = owl;

export class AccountReconcileMatchWidget extends Component {
    setup() {
        // Necessary in order to avoid a loop
        super.setup(...arguments);
        useSubEnv({
            config: {},
            parentController: this.env.parentController,
        });
    }
    get listViewProperties() {
        return {
            type: "list",
            display: {
                controlPanel: {
                    // Hiding the control panel buttons
                    "top-left": false,
                    "bottom-left": false,
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
