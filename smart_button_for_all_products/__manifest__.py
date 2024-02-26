# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Smart buttons for products",
    "summary": """ """,
    "version": "",
    "license": "LGPL-3",
    "author": "Dow Group",
    "website": "",
    "depends": ["base", "contacts", "sale", "mail",'stock','website_sale'],
    "data": [
        "security/ir.model.access.csv",
        "views/smart_res_partner.xml",
        "views/stock_picking.xml",
        "views/product_template.xml",
        "views/sale_order_line.xml",
        # "views/sale_order_report.xml",
        "views/website_cart_quantity.xml",
        "report/delivery_report.xml",
        "report/delivery_report_template.xml",
        'views/stock_move_details.xml'
        
    ],
}
