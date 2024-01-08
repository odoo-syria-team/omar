from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.sale.controllers.portal import CustomerPortal
import json


# pricelist form view
class PricelistTemplateFrom(http.Controller):
    @http.route('/new/catalogue', auth="user", csrf=False, website=True, methods=['GET', 'POST'])
    def get_document_record(self):
        user_pricelist_id = request.env['product.pricelist'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not user_pricelist_id:
            raise AccessDenied()
        if request.httprequest.method == 'POST':
            try:
                sale_id = request.env['sale.order'].sudo().create({
                    'partner_id': request.env.user.partner_id.id,
                    'pricelist_id': user_pricelist_id.id,
                    'state': 'draft',
                })
                self._write_vals(sale_id, user_pricelist_id)

                return request.redirect('/my/catalogue')

            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

        else:
            try:
                return request.render('catalogue_module.sale_order_form_create_from_pricelist', {
                    'page_name': 'sale_order_pricelist_form_page',
                    'pricelist_id': user_pricelist_id,
                })
            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

    def _write_vals(self, sale_id, user_pricelist_id):

        sale_order_vals = {}
        form = request.httprequest.form

        item_ids = user_pricelist_id.item_ids.filtered(lambda rec: str(rec.id) in form.keys())
        qty_dict = {}
        price_dict = {}
        form_dict = {}

        for key, value in zip(form.keys(), form.values()):
            form_dict[key] = form.getlist(key)

        for key, value in zip(form_dict.keys(), form_dict.values()):
            if 'qty_to_add' in key:
                qty_dict[int(key.split('qty_to_add')[0])] = value[0]
            if 'fixed_price' in key:
                price_dict[int(key.split('fixed_price')[0])] = value[0]
        order_line = [(0, 0, {
            'order_id': sale_id.id,
            'product_template_id': item.product_tmpl_id.id,
            'product_id': item.product_id.id,
            'product_uom_qty': qty_dict[item.id],
            'max_qty': item.qty_to_show,
            'product_uom': item.product_tmpl_id.uom_id.id,
            'name': item.product_tmpl_id.name,
            'price_unit': price_dict[item.id],

        }) for item in item_ids]
        sale_order_vals['order_line'] = order_line
        sale_order_vals['state'] = 'catalogue'
        sale_id.sudo().write(sale_order_vals)

    @http.route('/my/pricelist/available', type='http', auth="user", website=True, methods=['GET'], csrf=False)
    def show_pricelist_available(self):
        user_pricelist_id = request.env['product.pricelist'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        response_data = [{'display': 1 if user_pricelist_id else 0}]
        return json.dumps(response_data)


class WebsiteQuotationInherit(CustomerPortal):
    def _prepare_quotations_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'sent', 'cancel'])
        ]
