# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CharId(fields.Id):
    type = "string"
    column_type = ("varchar", fields.pg_varchar())


class AccountAccountReconcile(models.Model):
    _name = "account.account.reconcile"
    _description = "Account Account Reconcile"
    _inherit = "account.reconcile.abstract"
    _auto = False

    reconcile_data_info = fields.Serialized(inverse="_inverse_reconcile_data_info")

    partner_id = fields.Many2one("res.partner", readonly=True)
    account_id = fields.Many2one("account.account", readonly=True)
    name = fields.Char(readonly=True)
    is_reconciled = fields.Boolean(readonly=True)

    @property
    def _table_query(self):
        return "%s %s %s %s %s" % (
            self._select(),
            self._from(),
            self._where(),
            self._groupby(),
            self._having(),
        )

    def _select(self):
        account_account_name_field = self.env["ir.model.fields"].search(
            [("model", "=", "account.account"), ("name", "=", "name")]
        )
        account_name = (
            f"a.name ->> '{self.env.user.lang}'"
            if account_account_name_field.translate
            else "a.name"
        )
        return f"""
            SELECT
                min(aml.id) as id,
                MAX({account_name}) as name,
                aml.partner_id,
                a.id as account_id,
                FALSE as is_reconciled,
                aml.currency_id as currency_id,
                a.company_id,
                false as foreign_currency_id
        """

    def _from(self):
        return """
            FROM
                account_account a
                INNER JOIN account_move_line aml ON aml.account_id = a.id
                INNER JOIN account_move am ON am.id = aml.move_id
            """

    def _where(self):
        return """
            WHERE a.reconcile
                AND am.state = 'posted'
                AND aml.amount_residual != 0
        """

    def _groupby(self):
        return """
            GROUP BY
                a.id, aml.partner_id, aml.currency_id, a.company_id
        """

    def _having(self):
        return """
            HAVING
                SUM(aml.debit) > 0
                AND SUM(aml.credit) > 0
        """

    def _compute_reconcile_data_info(self):
        data_obj = self.env["account.account.reconcile.data"]
        for record in self:
            data_record = data_obj.search(
                [("user_id", "=", self.env.user.id), ("reconcile_id", "=", record.id)]
            )
            if data_record:
                record.reconcile_data_info = data_record.data
            else:
                record.reconcile_data_info = {"data": [], "counterparts": []}

    def _inverse_reconcile_data_info(self):
        data_obj = self.env["account.account.reconcile.data"]
        for record in self:
            data_record = data_obj.search(
                [("user_id", "=", self.env.user.id), ("reconcile_id", "=", record.id)]
            )
            if data_record:
                data_record.data = record.reconcile_data_info
            else:
                data_obj.create(
                    {
                        "reconcile_id": record.id,
                        "user_id": self.env.user.id,
                        "data": record.reconcile_data_info,
                    }
                )

    @api.onchange("add_account_move_line_id")
    def _onchange_add_account_move_line(self):
        if self.add_account_move_line_id:
            data = self.reconcile_data_info
            if self.add_account_move_line_id.id not in data["counterparts"]:
                data["counterparts"].append(self.add_account_move_line_id.id)
            else:
                del data["counterparts"][
                    data["counterparts"].index(self.add_account_move_line_id.id)
                ]
            self.reconcile_data_info = self._recompute_data(data)
            self.add_account_move_line_id = False

    @api.onchange("manual_reference", "manual_delete")
    def _onchange_manual_reconcile_reference(self):
        self.ensure_one()
        data = self.reconcile_data_info
        counterparts = []
        for line in data["data"]:
            if line["reference"] == self.manual_reference:
                if self.manual_delete:
                    continue
            counterparts.append(line["id"])
        data["counterparts"] = counterparts
        self.reconcile_data_info = self._recompute_data(data)
        self.manual_delete = False
        self.manual_reference = False

    def _recompute_data(self, data):
        new_data = {"data": [], "counterparts": data["counterparts"]}
        counterparts = data["counterparts"]
        amount = 0.0
        for line_id in counterparts:
            line = self._get_reconcile_line(
                self.env["account.move.line"].browse(line_id), "other", True, amount
            )
            new_data["data"].append(line)
            amount += line["amount"]
        return new_data

    def clean_reconcile(self):
        self.ensure_one()
        self.reconcile_data_info = {"data": [], "counterparts": []}

    def reconcile(self):
        lines = self.env["account.move.line"].browse(
            self.reconcile_data_info["counterparts"]
        )
        lines.reconcile()
        data_record = self.env["account.account.reconcile.data"].search(
            [("user_id", "=", self.env.user.id), ("reconcile_id", "=", self.id)]
        )
        data_record.unlink()


class AccountAccountReconcileData(models.TransientModel):
    _name = "account.account.reconcile.data"
    _description = "Reconcile data model to store user info"

    user_id = fields.Many2one("res.users", required=True)
    reconcile_id = fields.Integer(required=True)
    data = fields.Serialized()
