# -*- coding utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp import pooler
from datetime import datetime
from openerp.addons.report_webkit import webkit_report


class BankStatementWebkit(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(BankStatementWebkit, self).__init__(
            cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((
            _('BORDEREAU DE REMISE DE CHEQUES'),
            company.name, company.currency_id.name))
        footer_date_time = self.formatLang(
            str(datetime.today())[:19], date_time=True)
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'get_bank_statement': self._get_bank_statement_data,
            'report_name': _('BORDEREAU DE REMISE DE CHEQUES'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right',
                 ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_bank_statement_data(self, statement):
        statement_obj = self.pool.get('account.bank.statement.line')
        statement_line_ids = statement_obj.search(
            self.cr,
            self.uid,
            [('statement_id', '=', statement.id)])
        statement_lines = statement_obj.browse(
            self.cr, self.uid, statement_line_ids)
        return statement_lines

webkit_report.WebKitParser(
    'report.bank_statement_webkit', 'account.bank.statement',
    'addons/account_statement_ext/report/bank_statement_report.mako',
    parser=BankStatementWebkit)
