import {KanbanController} from "@web/views/kanban/kanban_controller";
import {ReconcileMoveLineControllerMixin} from "./reconcile_move_line_controller.esm.js";

export class ReconcileMoveLineKanbanController extends ReconcileMoveLineControllerMixin(
    KanbanController
) {}

ReconcileMoveLineKanbanController.template =
    "account_reconcile_oca.ReconcileMoveLineKanbanController";
