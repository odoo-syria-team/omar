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
        'web.assets_frontend': [
            'https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.3/jspdf.min.js',
            'catalogue_module/static/src/js/catalogue.js',
        ],
    },
    # always loaded
    'data': [
        'views/sale_order.xml',
        'views/price_list.xml',
        'views/portal/catalogue_template_form_portal.xml',
        'views/portal/catalogue_template_list_portal.xml',
        'views/portal/my_account_documents.xml',
        'report/report_info.xml',
        'report/catalogue_template.xml',
        'report/catalogue_template_pdf.xml',
        "views/portal/sale_order_form_create_from_pricelist.xml",

    ],

    # loaded in demo mode only
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    # 'post_init_hook': 'remove_contact_us_menu',
}
