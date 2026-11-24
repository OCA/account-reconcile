import {ReconcileMoveLineKanbanController} from "./reconcile_move_line_kanban_controller.esm.js";
import {ReconcileMoveLineKanbanRenderer} from "./reconcile_move_line_kanban_renderer.esm.js";
import {ReconcileMoveLineModel} from "./reconcile_move_line_model.esm.js";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export const ReconcileMoveLineKanbanView = {
    ...kanbanView,
    Controller: ReconcileMoveLineKanbanController,
    Model: ReconcileMoveLineModel,
    Renderer: ReconcileMoveLineKanbanRenderer,
    buttonTemplate: "reconcile_move_line.ListView.Buttons",
};

registry
    .category("views")
    .add("reconcile_move_line_kanban", ReconcileMoveLineKanbanView);
