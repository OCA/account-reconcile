/** @odoo-module */
import {Notebook} from "@web/core/notebook/notebook";
import {onWillDestroy} from "@odoo/owl";

export class ReconcileFormNotebook extends Notebook {
    setup() {
        super.setup(...arguments);
        const onPageNavigate = this.onPageNavigate.bind(this);
        this.env.bus.addEventListener("RECONCILE_PAGE_NAVIGATE", onPageNavigate);

        onWillDestroy(() => {
            this.env.bus.removeEventListener("RECONCILE_PAGE_NAVIGATE", onPageNavigate);
        });
    }
    onPageNavigate(ev) {
        for (const page of this.pages) {
            if (
                ev.detail.detail.name === page[1].name &&
                this.state.currentPage !== page[0]
            ) {
                ev.preventDefault();
                ev.detail.detail.originalEv.preventDefault();
                this.state.currentPage = page[0];
                return;
            }
        }
    }
}

ReconcileFormNotebook.props = {
    ...Notebook.props,
};
