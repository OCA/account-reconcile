/** @odoo-module */

import {ReconcileManualController} from "./reconcile_manual_controller.esm.js";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export const FormManualReconcileView = {
    ...formView,
    Controller: ReconcileManualController,
};

registry.category("views").add("reconcile_manual", FormManualReconcileView);
