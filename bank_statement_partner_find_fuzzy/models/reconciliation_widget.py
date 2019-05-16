# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def _get_bank_statement_line_partners(self, st_lines):
        results = super()._get_bank_statement_line_partners(st_lines)
        params = []

        # Add the res.partner's IR rules. In case partners are not shared
        # between companies, identical partners may exist in a company we
        # don't have access to.
        ir_rules_query = self.env['res.partner']._where_calc([])
        self.env['res.partner']._apply_ir_rules(ir_rules_query, 'read')
        from_clause, where_clause, where_clause_params = \
            ir_rules_query.get_sql()
        if where_clause:
            where_partner = ('WHERE %s' % where_clause).replace(
                'res_partner', 'p')
            params += where_clause_params
        else:
            where_partner = ''

        query = '''
             SELECT
                st_line.id AS id,
                p.id AS partner_id
            FROM account_bank_statement_line AS st_line
            JOIN res_partner p ON p.id IN (
                WITH Q AS (
                    SELECT id, name <-> st_line.partner_name as dist
                    FROM res_partner\n'''
        query += '%s' % where_partner
        query += '''ORDER BY dist LIMIT 1)\n'''
        query += 'select id from Q)\n'
        query += 'WHERE st_line.id IN %s'
        params += [tuple(st_lines.ids)]
        self._cr.execute(query, params)

        for res in self._cr.dictfetchall():
            results[res['id']] = res['partner_id']
        return results
