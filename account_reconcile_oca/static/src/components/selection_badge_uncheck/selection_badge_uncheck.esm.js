import {
    BadgeSelectionField,
    badgeSelectionField,
} from "@web/views/fields/badge_selection/badge_selection_field";
import {registry} from "@web/core/registry";

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

export const FieldSelectionBadgeUncheckField = {
    ...badgeSelectionField,
    component: FieldSelectionBadgeUncheck,
    supportedTypes: ["many2one"],
};
registry
    .category("fields")
    .add("selection_badge_uncheck", FieldSelectionBadgeUncheckField);
