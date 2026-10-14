import {badgesMany2oneField} from "@web/views/fields/badges_many2one/badges_many2one_field";
import {registry} from "@web/core/registry";

// Clicking on the selected badge unselects it, even if the field is required
// in the view (the core widget only allows it for optional fields).
export const FieldSelectionBadgeUncheckField = {
    ...badgesMany2oneField,
    extractProps(fieldInfo, dynamicInfo) {
        return {
            ...badgesMany2oneField.extractProps(fieldInfo, dynamicInfo),
            canDeselect: true,
        };
    },
};
registry
    .category("fields")
    .add("selection_badge_uncheck", FieldSelectionBadgeUncheckField);
