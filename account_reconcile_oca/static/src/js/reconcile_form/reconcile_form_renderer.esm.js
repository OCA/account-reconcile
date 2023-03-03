/** @odoo-module */

import {FormRenderer} from "@web/views/form/form_renderer";
import {ReconcileFormNotebook} from "./reconcile_form_notebook.esm.js";

export class ReconcileFormRenderer extends FormRenderer {}

ReconcileFormRenderer.components = {
    ...ReconcileFormRenderer.components,
    Notebook: ReconcileFormNotebook,
};
