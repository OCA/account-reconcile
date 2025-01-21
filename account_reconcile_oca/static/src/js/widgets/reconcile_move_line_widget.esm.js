import {View} from "@web/views/view";
import {evaluateBooleanExpr} from "@web/core/py_js/py";
import {getFieldContext} from "@web/model/relational_model/utils";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const {Component, useSubEnv} = owl;

export class AccountReconcileMatchWidget extends Component {
    setup() {
        // Necessary in order to avoid a loop
        useSubEnv({
            config: {},
            parentController: this.env.parentController,
        });
    }

    getDomain() {
        let domain = this.props.domain;
        if (typeof domain === "function") {
            domain = domain();
        }
        return domain;
    }
    get listViewProperties() {
        return {
            type: "list",
            display: {
                controlPanel: {
                    // Hiding the control panel buttons
                    "top-left": false,
                    "bottom-left": true,
                    layoutActions: false,
                },
            },
            noBreadcrumbs: true,
            resModel: this.props.record.fields[this.props.name].relation,
            searchMenuTypes: ["filter"],
            domain: this.getDomain(),
            context: {
                ...this.props.context,
                ...getFieldContext(this.props.record, this.props.name),
            },
            // Disables selector
            allowSelectors: false,
            // We need to force the search view in order to show the right one
            searchViewId: false,
            parentRecord: this.props.record,
            parentField: this.props.name,
            showButtons: false,
        };
    }
}
AccountReconcileMatchWidget.props = {
    ...standardFieldProps,
    placeholder: {type: String, optional: true},
    canOpen: {type: Boolean, optional: true},
    canCreate: {type: Boolean, optional: true},
    canWrite: {type: Boolean, optional: true},
    canQuickCreate: {type: Boolean, optional: true},
    canCreateEdit: {type: Boolean, optional: true},
    context: {type: String, optional: true},
    domain: {type: [Array, Function], optional: true},
    nameCreateField: {type: String, optional: true},
    searchLimit: {type: Number, optional: true},
    relation: {type: String, optional: true},
    string: {type: String, optional: true},
    canScanBarcode: {type: Boolean, optional: true},
    update: {type: Function, optional: true},
    value: {optional: true},
    decorations: {type: Object, optional: true},
};
AccountReconcileMatchWidget.template = "account_reconcile_oca.ReconcileMatchWidget";
AccountReconcileMatchWidget.components = {
    ...AccountReconcileMatchWidget.components,
    View,
};

export const AccountReconcileMatchWidgetField = {
    component: AccountReconcileMatchWidget,
    supportedTypes: [],
    extractProps({attrs, context, decorations, options}, dynamicInfo) {
        const hasCreatePermission = attrs.can_create
            ? evaluateBooleanExpr(attrs.can_create)
            : true;
        const hasWritePermission = attrs.can_write
            ? evaluateBooleanExpr(attrs.can_write)
            : true;
        const canCreate = options.no_create ? false : hasCreatePermission;
        return {
            placeholder: attrs.placeholder,
            canOpen: !options.no_open,
            canCreate,
            canWrite: hasWritePermission,
            canQuickCreate: canCreate && !options.no_quick_create,
            canCreateEdit: canCreate && !options.no_create_edit,
            context: context,
            decorations,
            domain: dynamicInfo.domain,
        };
    },
};

registry
    .category("fields")
    .add("account_reconcile_oca_match", AccountReconcileMatchWidgetField);
