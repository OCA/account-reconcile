/** @odoo-module */

import {ReconcileMoveLineController} from "./reconcile_move_line_controller.esm.js";
import {ReconcileMoveLineRenderer} from "./reconcile_move_line_renderer.esm.js";

import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export const ReconcileMoveLineView = {
    ...listView,
    Controller: ReconcileMoveLineController,
    Renderer: ReconcileMoveLineRenderer,
};

registry.category("views").add("reconcile_move_line", ReconcileMoveLineView);
