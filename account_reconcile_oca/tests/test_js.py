# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo
from odoo.tools import mute_logger

from odoo.addons.web.tests.test_js import WebSuite


@odoo.tests.tagged("post_install", "-at_install")
class TestAccountReconcileOCAJS(WebSuite):
    """Test Account Reconcile OCA JS code"""

    def get_hoot_filters(self):
        self._test_params = [("+", "@account_reconcile_oca")]
        return super().get_hoot_filters()

    @mute_logger(
        "odoo.addons.account_reconcile_oca.tests.test_js.TestAccountReconcileOCAJS.test_automation_oca"
    )
    def test_automation_oca(self):
        self.test_unit_desktop()
