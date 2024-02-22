# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Price list extension",
    "summary": """ """,
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "",
    "depends": ["sale", "crm"],
    "data": [
        "views/price_list.xml",
        # "views/portal/inherit_sale_order_form_portal.xml",
        "views/portal/inherit_sale_order_list_portal.xml",
        "views/portal/sale_order_form_create_from_pricelist.xml",
    ],
}
