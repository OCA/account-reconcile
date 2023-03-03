/** @odoo-module **/

import {ChatterContainer} from "@mail/components/chatter_container/chatter_container";
import {registry} from "@web/core/registry";

const {Component} = owl;

export class AccountReconcileChatterWidget extends Component {}
AccountReconcileChatterWidget.template =
    "account_reconcile_oca.AccountReconcileChatterWidget";
AccountReconcileChatterWidget.components = {...Component.components, ChatterContainer};

registry
    .category("fields")
    .add("account_reconcile_oca_chatter", AccountReconcileChatterWidget);
