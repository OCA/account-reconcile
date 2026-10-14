import {animationFrame, click, expect, test} from "@odoo/hoot";
import {
    clickSave,
    defineModels,
    fields,
    models,
    mountView,
} from "@web/../tests/web_test_helpers";
import {defineMailModels, startServer} from "@mail/../tests/mail_test_helpers";

class MainElement extends models.Model {
    _name = "main.element";
    child_id = fields.Many2one({relation: "child.element"});
    reconcile_data_info = fields.Json();
    _records = [
        {
            id: 1,
            reconcile_data_info: {
                counterparts: [1],
            },
        },
        {
            id: 2,
            reconcile_data_info: {
                counterparts: [],
            },
        },
    ];
}

class ChildElement extends models.Model {
    _name = "child.element";
    name = fields.Char();
    _records = [
        {
            id: 1,
            name: "value 1",
        },
        {
            id: 2,
            name: "value 2",
        },
    ];

    _views = {
        list: `
            <list js_class="reconcile_move_line"
                    create="0"
                    edit="0"
                    export_xlsx="false">
                <field name="name" />
            </list>
        `,
    };
}

defineModels([MainElement, ChildElement]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check selected item", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "main.element",
        arch: `
            <form>
                <field name="reconcile_data_info" invisible="1" />
                <field name="child_id" widget="account_reconcile_oca_match" />
            </form>`,
    });
    expect(`[name="child_id"]`).toHaveCount(1);
    expect(`[name="child_id"] .o_data_row`).toHaveCount(2);
    expect(
        `[name="child_id"] .o_data_row.o_field_account_reconcile_oca_move_line_selected`
    ).toHaveCount(1);
    expect(
        `[name="child_id"] .o_data_row.o_field_account_reconcile_oca_move_line_selected`
    ).toHaveText("value 1");
});
test("Check no selected item and click", async () => {
    // We don't check the selection, as that requires a onchange,
    // but we want to see that the field is modified.
    const pyEnv = await startServer();
    expect(pyEnv["main.element"].browse([2])[0].child_id).toBe(false);
    await mountView({
        type: "form",
        resId: 2,
        resIds: [2],
        resModel: "main.element",
        arch: `
            <form>
                <field name="reconcile_data_info" invisible="1" />
                <field name="child_id" widget="account_reconcile_oca_match" />
            </form>`,
    });
    expect(`[name="child_id"]`).toHaveCount(1);
    expect(`[name="child_id"] .o_data_row`).toHaveCount(2);
    expect(
        `[name="child_id"] .o_data_row.o_field_account_reconcile_oca_move_line_selected`
    ).toHaveCount(0);
    await click(`[name="child_id"] .o_data_row .o_data_cell:contains("value 2")`);
    await animationFrame();
    await clickSave();
    await animationFrame();
    expect(pyEnv["main.element"].browse([2])[0].child_id).toBe(2);
});
