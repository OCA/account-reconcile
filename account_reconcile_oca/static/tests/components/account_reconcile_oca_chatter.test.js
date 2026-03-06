import {animationFrame, click, expect, test} from "@odoo/hoot";
import {
    asyncStep,
    defineModels,
    fields,
    models,
    mountView,
    waitForSteps,
} from "@web/../tests/web_test_helpers";
import {
    contains,
    defineMailModels,
    insertText,
    onRpcBefore,
    startServer,
} from "@mail/../tests/mail_test_helpers";

class MainElement extends models.Model {
    _name = "main.element";
    related_id = fields.Many2one({relation: "child.element"});
    _records = [
        {
            id: 1,
            related_id: 1,
        },
    ];
}

class ChildElement extends models.Model {
    _name = "child.element";
    _inherit = ["mail.thread"];
    name = fields.Char();
    _records = [
        {
            id: 1,
            name: "value 1",
        },
    ];
}

// As we use mail as a dependancy, we need to declare models.
defineMailModels();
defineModels([MainElement, ChildElement]);

test("Check Chatter from Child Model", async () => {
    onRpcBefore("/mail/message/post", (args) => {
        asyncStep("/mail/message/post");
        const expected = {
            context: args.context,
            post_data: {
                body: "hey",
                email_add_signature: true,
                message_type: "comment",
                subtype_xmlid: "mail.mt_comment",
            },
            thread_id: 1,
            thread_model: "child.element",
        };
        expect(args).toEqual(expected);
    });
    const pyEnv = await startServer();
    pyEnv["mail.message"].create({
        model: "child.element",
        res_id: 1,
        body: "test message",
    });
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "main.element",
        arch: `
            <form>
                <field name="related_id" widget="account_reconcile_oca_chatter" />
            </form>`,
    });
    expect(`[name="related_id"]`).toHaveCount(1);
    await animationFrame();
    await contains(`[name="related_id"] .o-mail-Message-body`);
    expect(`[name="related_id"] .o-mail-Message-body`).toHaveCount(1);
    await click(".o-mail-Chatter-sendMessage");
    await animationFrame();
    await insertText(".o-mail-Composer-input", "hey");
    await click(".o-mail-Composer-send:enabled");
    await waitForSteps(["/mail/message/post"]);
});
