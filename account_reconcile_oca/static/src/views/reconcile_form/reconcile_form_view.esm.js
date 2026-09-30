import {ReconcileFormController} from "./reconcile_form_controller.esm.js";
import {ReconcileFormRenderer} from "./reconcile_form_renderer.esm.js";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export const ReconcileFormView = {
    ...formView,
    Controller: ReconcileFormController,
    Renderer: ReconcileFormRenderer,
};

registry.category("views").add("reconcile_form", ReconcileFormView);
