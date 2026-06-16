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
        data[this.props.parentField] = {
            id: record.resId,
            display_name: record.display_name,
        };
        await this.props.parentRecord.update(data);
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
        await this.props.parentRecord.save();
        await this.model.orm.call(
            this.props.parentRecord.resModel,
            "add_multiple_lines",
            [this.props.parentRecord.resIds, this.model.root.domain]
        );
        await this.props.parentRecord.load();
        this.props.parentRecord.model.notify();
    }
}

ReconcileMoveLineController.template = `account_reconcile_oca.ReconcileMoveLineController`;
ReconcileMoveLineController.props = {
    ...ListController.props,
    parentRecord: {type: Object, optional: true},
    parentField: {type: String, optional: true},
};
