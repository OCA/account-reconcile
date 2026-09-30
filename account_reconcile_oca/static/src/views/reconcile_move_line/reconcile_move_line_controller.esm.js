import {ListController} from "@web/views/list/list_controller";

export class ReconcileMoveLineController extends ListController {
    async openRecord(record) {
        // Selecting a counterpart updates the parent record, which re-renders
        // the whole reconcile form and reloads this list. Keep the scroll
        // position of the right panel so the user stays where they were (the
        // current page is preserved by ReconcileMoveLineModel).
        const scroller = document.querySelector(".o_account_reconcile_oca_info");
        const scrollTop = scroller ? scroller.scrollTop : null;
        var data = {};
        data[this.env.reconcileParent.field] = {
            id: record.resId,
            display_name: record.display_name,
        };
        await this.env.reconcileParent.record.update(data);
        if (scroller && scrollTop !== null) {
            // The update re-renders the form asynchronously, so restore the
            // scroll across the next couple of frames to make sure it sticks
            // once the DOM has been patched.
            const restore = () => {
                scroller.scrollTop = scrollTop;
            };
            restore();
            requestAnimationFrame(() => {
                restore();
                requestAnimationFrame(restore);
            });
        }
    }
    async clickAddAll() {
        const parentRecord = this.env.reconcileParent.record;
        await parentRecord.save();
        await this.model.orm.call(parentRecord.resModel, "add_multiple_lines", [
            parentRecord.resIds,
            this.model.root.domain,
        ]);
        await parentRecord.load();
        parentRecord.model.notify();
    }
}
