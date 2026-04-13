import {animationFrame, click, expect, test} from "@odoo/hoot";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class MainElement extends models.Model {
    _name = "main.element";
    child_id = fields.Many2one({relation: "child.element"});
    _records = [
        {
            id: 1,
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
}

defineModels([MainElement, ChildElement]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check Badge Selection and management", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "main.element",
        arch: `
            <form>
                <field name="child_id" widget="selection_badge_uncheck" />
            </form>`,
    });
    expect(`[name="child_id"]`).toHaveCount(1);
    expect(`[name="child_id"] .o_selection_badge`).toHaveCount(2);
    expect(`[name="child_id"] .o_selection_badge.active`).toHaveCount(0);
    await click(`[name="child_id"] .o_selection_badge:contains("value 1")`);
    await animationFrame();
    expect(`[name="child_id"] .o_selection_badge.active`).toHaveCount(1);
    expect(`[name="child_id"] .o_selection_badge.active`).toHaveText("value 1");
});
