import {RelationalModel} from "@web/model/relational_model/relational_model";
import {deepEqual} from "@web/core/utils/objects";

// Keys of the model config that change what is actually fetched from the
// server. If none of them changes, a reload is a pure round trip.
const QUERY_KEYS = [
    "domain",
    "context",
    "groupBy",
    "orderBy",
    "offset",
    "limit",
    "comparison",
];

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

    /**
     * `useModel` reloads the list on every `onWillUpdateProps`, and this list is
     * a child of the reconcile form: selecting another statement line re-renders
     * the form *before* the new record is read, so the list is asked to reload
     * with the domain and the context of the line we are leaving. That request
     * fetches exactly what is already displayed and is thrown away ~150 ms
     * later, when the new record arrives and the real reload happens.
     *
     * So we skip the reload when the resulting config would fetch the very same
     * data. Only the props driven reloads are candidates to be skipped: an
     * explicit `model.load()` (the reload after an unlink, a multi edit, ...)
     * carries no domain and always goes through.
     */
    async load(params = {}) {
        if (this.root && "domain" in params) {
            const nextConfig = this._getNextConfig(this.config, params);
            const sameQuery = QUERY_KEYS.every((key) =>
                deepEqual(this.config[key], nextConfig[key])
            );
            if (sameQuery) {
                return;
            }
        }
        return super.load(params);
    }
}
