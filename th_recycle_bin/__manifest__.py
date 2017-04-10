# -*- coding: utf-8 -*-
{
    'name': "Recycle Bin",

    'summary': """
        Recycle bin for Records""",

    'description': """
        Recycle bin for records
    """,

    'author': "Tech Heliconia",
    'website': "https://tech.heliconia.in",

    'category': 'Tools',
    'version': '10.0.0.1',

    'depends': ['base'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}