import {animationFrame, click, expect, test} from "@odoo/hoot";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";
import {queryAllTexts} from "@odoo/hoot-dom";

class MainElement extends models.Model {
    _name = "main.element";

    name = fields.Char();

    _views = {
        kanban: `
            <kanban js_class="reconcile">
                <templates>
                    <t t-name="card">
                        <div class="o_kanban_record_title" t-att-data-id="record.name.raw_value"><field name="name"/></div>
                    </t>
                </templates>
            </kanban>
        `,
        form: `
            <form>
                <group><field name="name"/></group>
            </form>
        `,
    };
    _records = [
        {id: 1, name: "value 1"},
        {id: 2, name: "value 2"},
    ];
}

defineModels([MainElement]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check Kanban View", async () => {
    await mountView({
        type: "kanban",
        resIds: [1, 2],
        resModel: "main.element",
    });
    expect(".o_kanban_record .o_kanban_record_title").toHaveCount(2);
    expect(queryAllTexts(".o_kanban_record .o_kanban_record_title")).toEqual([
        "value 1",
        "value 2",
    ]);
    expect(".o_account_reconcile_oca_info .o_form_view").toHaveCount(0);
    await click(".o_kanban_record .o_kanban_record_title");
    await animationFrame();
    expect(".o_account_reconcile_oca_info .o_form_view").toHaveCount(1);
    expect(
        queryAllTexts(
            ".o_kanban_record.o_kanban_record_reconcile_oca_selected .o_kanban_record_title"
        )
    ).toEqual(["value 1"]);
    await animationFrame();
    expect(
        ".o_account_reconcile_oca_info .o_form_view .o_field_widget[name='name'] input"
    ).toHaveValue("value 1");
    await click(".o_kanban_record .o_kanban_record_title[data-id='value 2']");
    await animationFrame();
    expect(
        queryAllTexts(
            ".o_kanban_record.o_kanban_record_reconcile_oca_selected .o_kanban_record_title"
        )
    ).toEqual(["value 2"]);
    await animationFrame();
    expect(
        ".o_account_reconcile_oca_info .o_form_view .o_field_widget[name='name'] input"
    ).toHaveValue("value 2");
});
