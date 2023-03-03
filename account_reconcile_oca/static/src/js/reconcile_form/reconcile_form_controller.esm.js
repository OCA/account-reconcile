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
    async reloadFormController() {
        var is_reconciled = this.model.root.data.is_reconciled;
        await this.model.root.load();
        if (!is_reconciled && this.model.root.data.is_reconciled) {
            // This only happens when we press the reconcile button
            if (this.env.parentController) {
                // Showing rainbow man
                const message = await this.orm.call(
                    "account.journal",
                    "get_rainbowman_message",
                    [[this.model.root.data.journal_id[0]]]
                );
                if (message) {
                    this.env.parentController.setRainbowMan(message);
                }
                // Refreshing
                await this.env.parentController.model.root.load();
                await this.env.parentController.render(true);
                this.env.parentController.selectRecord();
            }
        }
    }
}
