# -*- coding: utf-8 -*-
{
    "name": "Bloqueo de datos fiscales en facturas",
    "version": "16.0.0.0.1",
    "summary": "Bloquea los datos fiscales en las facturas existentes",
    "description": "Este módulo bloquea la actualización de los datos fiscales en las facturas existentes",
    "category": "Accounting",
    "author": "Qubiq",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["base", "account"],
    "data": ["views/account_move.xml", "views/report_invoice_custom.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
