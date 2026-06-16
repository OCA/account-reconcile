import {RelationalModel} from "@web/model/relational_model/relational_model";

export class ReconcileMoveLineModel extends RelationalModel {
    /**
     * The candidates list lives inside the reconcile form. Every time the user
     * selects a counterpart the parent record is updated, the whole form
     * re-renders and passes a brand new (but value-wise identical) domain to
     * this list. RelationalModel resets the pagination offset to 0 whenever it
     * is reloaded "from above with a domain", which sent the user back to the
     * first page of candidates on every click.
     *
     * We drop the domain from the reload params when it didn't actually change,
     * so the offset (current page) is preserved. A real search change still
     * carries a different domain value and resets the page as expected.
     */
    _getNextConfig(currentConfig, params) {
        if (
            params.domain &&
            currentConfig.domain &&
            JSON.stringify(params.domain) === JSON.stringify(currentConfig.domain)
        ) {
            params = {...params};
            delete params.domain;
        }
        return super._getNextConfig(currentConfig, params);
    }
}
