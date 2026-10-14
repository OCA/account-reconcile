import {Component, useProps} from "@odoo/owl";
import {Chatter} from "@mail/chatter/web_portal_project/chatter";

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class AccountReconcileChatterWidget extends Component {
    props = useProps(standardFieldProps);
}
AccountReconcileChatterWidget.template =
    "account_reconcile_oca.AccountReconcileChatterWidget";
AccountReconcileChatterWidget.components = {...Component.components, Chatter};
export const AccountReconcileChatterWidgetField = {
    component: AccountReconcileChatterWidget,
    supportedTypes: ["many2one"],
};
registry
    .category("fields")
    .add("account_reconcile_oca_chatter", AccountReconcileChatterWidgetField);
