/** @odoo-module */

import {ReconcileController} from "./reconcile_controller.esm.js";
import {ReconcileRenderer} from "./reconcile_renderer.esm.js";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export const reconcileView = {
    ...kanbanView,
    Renderer: ReconcileRenderer,
    Controller: ReconcileController,
    buttonTemplate: "account_reconcile.ReconcileView.Buttons",
    searchMenuTypes: ["filter"],
};

registry.category("views").add("reconcile", reconcileView);
