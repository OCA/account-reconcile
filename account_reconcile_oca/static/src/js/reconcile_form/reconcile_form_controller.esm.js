/** @odoo-module */

import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";
import {useViewButtons} from "@web/views/view_button/view_button_hook";
const {useRef} = owl;

export class ReconcileFormController extends FormController {
    setup() {
        super.setup(...arguments);
        this.env.exposeController(this);
        this.orm = useService("orm");
        const rootRef = useRef("root");
        useViewButtons(this.model, rootRef, {
            reload: this.reloadFormController.bind(this),
            beforeExecuteAction: this.beforeExecuteActionButton.bind(this),
            afterExecuteAction: this.afterExecuteActionButton.bind(this),
        });
    }
    displayName() {
        return this.env.config.getDisplayName();
    }
    async reloadFormController() {
        var is_reconciled = this.model.root.data.is_reconciled;
        await this.model.root.load();
        if (this.env.parentController) {
            // We will update the parent controller every time we reload the form.
            await this.env.parentController.model.root.load();
            await this.env.parentController.render(true);
            if (!is_reconciled && this.model.root.data.is_reconciled) {
                // This only happens when we press the reconcile button for showing rainbow man
                const message = await this.orm.call(
                    "account.journal",
                    "get_rainbowman_message",
                    [[this.model.root.data.journal_id[0]]]
                );
                if (message) {
                    this.env.parentController.setRainbowMan(message);
                }
                // Refreshing
                this.env.parentController.selectRecord();
            }
        }
    }
}
