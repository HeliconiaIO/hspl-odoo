{
    'name': 'Stock Movement',
    'summary': """Stock Movement""",
    'version': '1.0',
    'description': """This module is for stock_movement report generation""",
    'author': 'Tech heliconia',
    'company': 'Tech heliconia Solutions',
    'website': 'https://tech.heliconia.in',
    'category': 'Tools',
    'depends': ['base', 'stock', 'product', 'sales_team'],
    'data': [
        'view/view.xml',
        'wizard/wizard_view.xml',
        'report/slow_moving_product_report.xml',
        'report/slow_moving_product_report_definition.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
