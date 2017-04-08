# -*- coding: utf-8 -*-
# Part of Tech Heliconia. See LICENSE file for copyright and licensing details.

{
    'name': "Sales History",
    'summary': """
    Customer sales history on sale order form
    """,
    'description': """
    Adds a button to show customer sales history on sale order form,
    History list enables user to add past purchased product in to
    sale order line easily.
    """,
    'author': "Tech Heliconia",
    'website': "https://tech.heliconia.in",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'wizard/history_view.xml',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
