{
    'name': 'Vendor Market Management',
    'summary': '',
    'description': "Allow vendor to request for ability to add his products on the dashboard from website",
    'author': 'Omar Doukmak',
    'website': 'omar.doukmak.computerscience@gmail.com , +963 930 462 613',

    # category can be used to filter modules in modules listing
    'category': 'Inventory',
    'version': '0.1',

    # any module for this one to work correctly
    'depends': ['contacts', 'base', 'mail', 'web', 'website', 'stock'],
    'assets': {
        # 'web.assets_frontend': [
        #     "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        # ],

    },
    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'data/mail_template.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/portal/product_template_form_portal.xml',
        'views/portal/product_template_list_portal.xml',
        'views/portal/my_account_documents.xml',
        'views/portal/vendor_request_form.xml',

    ],

    # loaded in demo mode only
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    # 'post_init_hook': 'remove_contact_us_menu',
}
