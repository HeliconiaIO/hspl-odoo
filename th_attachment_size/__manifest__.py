# -*- coding: utf-8 -*-
{
    'name': "TH Attachment Size",

    'summary': """
        Compute Attachment size in ir.attchament""",

    'description': """
        Compute Attachment size in ir.attchament
    """,

    'author': "Mihir Dabgar -Tech Heliconia",
    'website': "http://heliconia.in/",

    'category': 'base',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}