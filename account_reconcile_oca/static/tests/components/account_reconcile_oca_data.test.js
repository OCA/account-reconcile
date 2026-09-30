import {animationFrame, click, expect, test} from "@odoo/hoot";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class MainElement extends models.Model {
    _name = "main.element";
    reconcile_data_info = fields.Json();
    currency_id = fields.Many2one({relation: "res.currency"});
    company_currency_id = fields.Many2one({relation: "res.currency"});
    manual_reference = fields.Char();
    manual_delete = fields.Boolean();
    _views = {
        form: `
            <form>
                <field name="reconcile_data_info" widget="account_reconcile_oca_data"/>
                <field name="currency_id" invisible="1"/>
                <field name="company_currency_id" invisible="1"/>
                <field name="manual_reference" />
                <field name="manual_delete" />
            </form>
            `,
    };
    _records = [
        {
            id: 1,
            reconcile_data_info: {
                data: [
                    {
                        reference: "reconcile_auxiliary;1",
                        id: false,
                        account_id: [1, "Account 01"],
                        partner_id: false,
                        date: "2024-01-01",
                        name: "FIRST LINE",
                        amount: 100,
                        debit: 100,
                        credit: 0,
                        kind: "liquidity",
                        currency_id: 1,
                        line_currency_id: 1,
                        currency_amount: 100,
                    },
                    {
                        reference: "reconcile_auxiliary;2",
                        id: false,
                        account_id: [2, "Account 02"],
                        partner_id: false,
                        date: "2024-01-01",
                        name: "SECOND LINE",
                        amount: -100,
                        debit: 0,
                        credit: 100,
                        kind: "other",
                        currency_id: 1,
                        line_currency_id: 1,
                        currency_amount: -100,
                    },
                ],
            },
            currency_id: 1,
            company_currency_id: 1,
        },
    ];
}

class Currency extends models.Model {
    _name = "res.currency";

    name = fields.Char();
    symbol = fields.Char({string: "Currency Sumbol"});
    position = fields.Selection({
        selection: [
            ["after", "A"],
            ["before", "B"],
        ],
    });
    inverse_rate = fields.Float();

    _records = [{id: 1, name: "USD", symbol: "$", position: "before", inverse_rate: 1}];
}

defineModels([Currency, MainElement]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check Data info handling", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "main.element",
    });
    expect(`[name="reconcile_data_info"]`).toHaveCount(1);
    expect(`[name="reconcile_data_info"] .o_reconcile_widget_line`).toHaveCount(2);
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:first-child .o_account_reconcile_oca_data_line_name`
    ).toHaveText("FIRST LINE");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:first-child .o_account_reconcile_oca_data_line_debit`
    ).toHaveText("$ 100.00");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .o_account_reconcile_oca_data_line_name`
    ).toHaveText("SECOND LINE");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .o_account_reconcile_oca_data_line_credit`
    ).toHaveText("$ 100.00");

    expect(`[name="manual_reference"] input`).toHaveValue("");
    expect(`[name="manual_delete"] input`).not.toBeChecked();
    await click(`[name="reconcile_data_info"] .o_reconcile_widget_line:first-child`);
    await animationFrame();
    expect(`[name="manual_reference"] input`).toHaveValue("reconcile_auxiliary;1");
    await animationFrame();
    expect(`[name="manual_delete"] input`).not.toBeChecked();
});

test("Delete Line", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "main.element",
    });
    expect(`[name="reconcile_data_info"]`).toHaveCount(1);
    expect(`[name="reconcile_data_info"] .o_reconcile_widget_line`).toHaveCount(2);
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:first-child .o_account_reconcile_oca_data_line_name`
    ).toHaveText("FIRST LINE");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:first-child .o_account_reconcile_oca_data_line_debit`
    ).toHaveText("$ 100.00");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:first-child .fa-trash-o`
    ).toHaveCount(0);
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .o_account_reconcile_oca_data_line_name`
    ).toHaveText("SECOND LINE");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .o_account_reconcile_oca_data_line_credit`
    ).toHaveText("$ 100.00");
    expect(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .fa-trash-o`
    ).toHaveCount(1);
    expect(`[name="manual_reference"] input`).toHaveValue("");
    expect(`[name="manual_delete"] input`).not.toBeChecked();
    await click(
        `[name="reconcile_data_info"] .o_reconcile_widget_line:last-child .fa-trash-o`
    );
    await animationFrame();
    expect(`[name="manual_reference"] input`).toHaveValue("reconcile_auxiliary;2");
    await animationFrame();
    expect(`[name="manual_delete"] input`).toBeChecked();
});
