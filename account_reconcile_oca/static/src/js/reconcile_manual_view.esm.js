/** @odoo-module */

import {FormController} from "@web/views/form/form_controller";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useViewButtons} from "@web/views/view_button/view_button_hook";
const {useRef} = owl;

export class FormManualReconcileController extends FormController {
    setup() {
        super.setup(...arguments);
        const rootRef = useRef("root");
        useViewButtons(this.model, rootRef, {
            reload: this.reloadFormController.bind(this),
            beforeExecuteAction: this.beforeExecuteActionButton.bind(this),
            afterExecuteAction: this.afterExecuteActionButton.bind(this),
        });
    }
    async reloadFormController() {
        try {
            await this.model.root.load();
        } catch (error) {
            // This should happen when we reconcile a line (no more possible data...)
            if (this.env.parentController) {
                await this.env.parentController.model.root.load();
                await this.env.parentController.render(true);
                this.env.parentController.selectRecord();
            }
        }
    }
}

export const FormManualReconcileView = {
    ...formView,
    Controller: FormManualReconcileController,
};

registry.category("views").add("reconcile_manual", FormManualReconcileView);
