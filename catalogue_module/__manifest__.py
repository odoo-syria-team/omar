{
    'name': 'Catalog Module',
    'summary': '',
    'description': "Allow user to see products from sale order as catalogue",
    'author': 'Omar Doukmak',
    'website': 'omar.doukmak.computerscience@gmail.com , +963 930 462 613',

    # category can be used to filter modules in modules listing
    'category': 'sale',
    'version': '0.1',

    # any module for this one to work correctly
    'depends': ['contacts', 'base', 'mail', 'web', 'website', 'stock', 'sale'],
    'assets': {
        # 'web.assets_frontend': [
        #     "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        # ],

    },
    # always loaded
    'data': [
        'views/sale_order.xml',
        'views/portal/catalogue_template_form_portal.xml',
        'views/portal/catalogue_template_list_portal.xml',
        'views/portal/my_account_documents.xml',
        'report/report_info.xml',
        'report/catalogue_template.xml',
        'report/catalogue_template_pdf.xml',

    ],

    # loaded in demo mode only
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    # 'post_init_hook': 'remove_contact_us_menu',
}
