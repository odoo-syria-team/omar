# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Change Currency',
    'version': '1.0',
    'sequence': -200,
    'category': 'Sales',
    'depends': ['base', 'account'],
    'data': [
        'views/sale_order.xml',
        # 'report/report_info.xml',
        # 'report/sale_order_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
