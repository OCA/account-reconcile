/** @odoo-module **/

// import {ChatterContainer} from "@mail/components/chatter_container/chatter_container";
// import {Chatter} from "@mail/core/web/chatter";
import {Chatter} from "@mail/core/web/chatter";

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const {Component} = owl;

export class AccountReconcileChatterWidget extends Component {}
AccountReconcileChatterWidget.props = {...standardFieldProps};
AccountReconcileChatterWidget.template =
    "account_reconcile_oca.AccountReconcileChatterWidget";
AccountReconcileChatterWidget.components = {...Component.components, Chatter};
export const AccountReconcileChatterWidgetField = {
    component: AccountReconcileChatterWidget,
    supportedTypes: [],
};
registry
    .category("fields")
    .add("account_reconcile_oca_chatter", AccountReconcileChatterWidgetField);
