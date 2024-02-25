{
    'name': 'Dynamic Financial Reports Inherit',
    'version': '1.0',
    'category': 'Accounting',
    'summary': """Dynamic Financial Reports with drill 
                down and filters– Community Edition""",
    'description': "Dynamic Financial Reports, DynamicFinancialReports, FinancialReport, Accountingreports, odoo reports, odoo"
                   "This module creates dynamic Accounting General Ledger, Trial Balance, Balance Sheet "
                   "Proft and Loss, Cash Flow Statements, Partner Ledger,"
                   "Partner Ageing, Day book"
                   "Bank book and Cash book reports in Odoo 14 community edition.",
    'author': 'Omar Doukmak',
    'website': "omar.doukmak.computescience@gmail.com",
    'depends': ['base', 'base_accounting_kit', 'dynamic_accounts_report'],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dynamic_accounts_report_inherit/static/src/js/partner_ledger.js',
            # 'dynamic_accounts_report_inherit/static/src/xml/templates.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
