import {ReconcileMoveLineController} from "./reconcile_move_line_controller.esm.js";
import {ReconcileMoveLineModel} from "./reconcile_move_line_model.esm.js";
import {ReconcileMoveLineRenderer} from "./reconcile_move_line_renderer.esm.js";

import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export const ReconcileMoveLineView = {
    ...listView,
    Controller: ReconcileMoveLineController,
    Model: ReconcileMoveLineModel,
    Renderer: ReconcileMoveLineRenderer,
    buttonTemplate: "reconcile_move_line.ListView.Buttons",
};

registry.category("views").add("reconcile_move_line", ReconcileMoveLineView);
