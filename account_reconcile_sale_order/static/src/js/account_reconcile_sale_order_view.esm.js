/** @odoo-module */

import {ReconcileSaleOrderController} from "./account_reconcile_sale_order_controller.esm.js";
import {ReconcileSaleOrderRenderer} from "./account_reconcile_sale_order_renderer.esm.js";

import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export const ReconcileSaleOrderView = {
    ...listView,
    Controller: ReconcileSaleOrderController,
    Renderer: ReconcileSaleOrderRenderer,
    buttonTemplate: "reconcile_sale_order.ListView.Buttons",
};

registry.category("views").add("reconcile_sale_order", ReconcileSaleOrderView);
