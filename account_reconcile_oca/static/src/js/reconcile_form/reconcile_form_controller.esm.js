import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";
import {useViewButtons} from "@web/views/view_button/view_button_hook";
import {FetchRecordError} from "@web/model/relational_model/errors";
const {useRef} = owl;

export class ReconcileFormController extends FormController {
    setup() {
        super.setup(...arguments);
        this.env.exposeController(this);
        this.orm = useService("orm");
        const rootRef = useRef("root");
        useViewButtons(rootRef, {
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
        var forceRefresh = false;
        const journalId = this.model.root.data.journal_id;
        try {
            await this.model.root.load();
        } catch (e) {
            // If the record is not found, we need to reload the parent controller
            if (e instanceof FetchRecordError) {
                forceRefresh = true;
            } else {
                throw e;
            }
        }
        if (
            this.env.parentController &&
            (forceRefresh || (!is_reconciled && this.model.root.data.is_reconciled))
        ) {
            // We will update the parent controller every time we reload the form.
            await this.env.parentController.model.root.load();
            await this.env.parentController.render(true);
            if (journalId) {
                // This only happens when we press the reconcile button for showing rainbow man
                // Should not affect if we are in the reconcile view
                const message = await this.orm.call(
                    "account.journal",
                    "get_rainbowman_message",
                    [[journalId[0]]]
                );
                if (message) {
                    this.env.parentController.setRainbowMan(message);
                }
            }
            // Refreshing
            this.env.parentController.selectRecord();
        }
    }
}
