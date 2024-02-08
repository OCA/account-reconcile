/** @odoo-module **/
import {
    BadgeSelectionField,
    preloadSelection,
} from "@web/views/fields/badge_selection/badge_selection_field";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class FieldSelectionBadgeUncheck extends BadgeSelectionField {
    async onChange(value) {
        var old_value = this.props.value;
        if (this.props.type === "many2one") {
            old_value = old_value[0];
        }
        if (value === old_value) {
            this.props.update(false);
            return;
        }
        super.onChange(...arguments);
    }
}

FieldSelectionBadgeUncheck.props = {...standardFieldProps};
FieldSelectionBadgeUncheck.supportedTypes = ["many2one", "selection"];
FieldSelectionBadgeUncheck.additionalClasses = ["o_field_selection_badge"];

export const FieldSelectionBadgeUncheckField = {
    component: FieldSelectionBadgeUncheck,
    supportedTypes: ["many2one"],
};
registry
    .category("fields")
    .add("selection_badge_uncheck", FieldSelectionBadgeUncheckField);

registry.category("preloadedData").add("selection_badge_uncheck", {
    loadOnTypes: ["many2one"],
    preload: preloadSelection,
});
