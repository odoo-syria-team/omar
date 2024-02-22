from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.portal.controllers.portal import pager
from odoo.addons.portal.controllers import portal
import base64
from datetime import datetime
import json


# catalogue list view
class CatalogueTemplate(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CatalogueTemplate, self)._prepare_home_portal_values(counters)
        values['catalogue_count'] = request.env['sale.order'].search_count(
            [('state', '=', 'catalogue')])
        return values

    @http.route(['/my/catalogue', '/my/catalogue/page/<int:page>'], auth="user", csrf=False, website=True,
                methods=['GET'])
    def get_catalogue(self, sortby='name', page=1, search='', search_in='Catalogue'):

        try:
            sorted_list = {
                'id': {'label': 'Latest', 'order': 'id desc'},
                'name': {'label': 'Product', 'order': 'name'},
            }
            default_order_by = sorted_list[sortby]['order']
            search_list = {
                'Catalogue':
                    {
                        'label': 'Catalogue',
                        'input': 'Catalogue',
                        'domain': [('name', 'ilike', search), ('partner_id', '=', request.env.user.partner_id.id),
                                   ('state', '=', 'catalogue')]
                    },
            }
            search_domain = search_list[search_in]['domain']

            total_catalogue_ids = http.request.env['sale.order'].sudo().search_count(search_domain)

            page_details = pager(url='/my/catalogue',
                                 total=total_catalogue_ids,
                                 page=page,
                                 url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
                                 step=10
                                 )
            catalogue_ids = http.request.env['sale.order'].sudo().search(search_domain,
                                                                         limit=10, order=default_order_by,
                                                                         offset=page_details['offset'])
            if not catalogue_ids:
                return request.redirect('/my/home')
            return request.render('catalogue_module.catalogue_list', {
                'user_id': request.env.user,
                'page_name': 'catalogue_list_page',
                'catalogue_ids': catalogue_ids,
                'pager': page_details,
                'sortby': sortby,
                'search_in': search_in,
                'search': search,
                'searchbar_inputs': search_list,
                'searchbar_sortings': sorted_list
            })
        except UserError as e:
            return str(e)
        except Exception as e:
            return str(e)

    # catalogue form view
    @http.route('/my/catalogue/<int:catalogue_id>', auth="user", csrf=False, website=True, methods=['GET', 'POST'])
    def get_product_record(self, catalogue_id):
        try:
            user_catalogue_id = request.env['sale.order'].sudo().search(
                [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
            if not user_catalogue_id:
                raise AccessDenied()

        except UserError as e:
            return str(e)
        except Exception as e:
            return str(e)

        if request.httprequest.method == 'POST':
            # try:
            self._write_vals(user_catalogue_id)

            return request.redirect('/my/catalogue')

        # except UserError as e:
        #     return str(e)
        # except Exception as e:
        #     return str(e)

        if request.httprequest.method == 'GET':
            try:
                if catalogue_id != -1 and catalogue_id not in user_catalogue_id.ids:
                    raise AccessDenied()

                product_ids = user_catalogue_id.pricelist_id.item_ids.mapped('product_tmpl_id').filtered(
                    lambda product_id: product_id not in user_catalogue_id.order_line.mapped('product_template_id'))

                return request.render('catalogue_module.catalogue_form', {
                    'user_id': request.env.user,
                    'page_name': 'catalogue_form_page',
                    'o': user_catalogue_id,
                    'product_ids': product_ids,
                })
            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

    def _write_vals(self, user_catalogue_id):

        form_dict = {}
        form = request.httprequest.form

        catalogue_to_delete = []
        line_id = 0
        product_id = 0
        for key, value in zip(form.keys(), form.values()):
            form_dict[key] = form.getlist(key)
        for key, value in zip(form_dict.keys(), form_dict.values()):
            catalogue_vals = {}
            order_line_vals = {}
            if 'delete' in key:
                catalogue_to_delete.append(int(key.split('delete')[0]))
                continue

            if 'product_uom_qty' in key:
                if '-' in key:
                    order_line_vals['product_uom_qty'] = value[0]
                    product_id = int(key.split('-product_uom_qty')[0])
                else:
                    catalogue_vals['product_uom_qty'] = value[0]
                    line_id = int(key.split('product_uom_qty')[0])

            if 'price_unit' in key:
                if '-' in key:
                    order_line_vals['price_unit'] = value[0]
                    product_id = int(key.split('-price_unit')[0])
                else:
                    catalogue_vals['price_unit'] = value[0]
                    line_id = int(key.split('price_unit')[0])
            if product_id != 0 and product_id not in user_catalogue_id.order_line.mapped('product_template_id').ids:
                my_line = user_catalogue_id.pricelist_id.item_ids.filtered(
                    lambda item: item.product_tmpl_id.id == product_id)
                order_line = [(0, 0, {
                    'order_id': user_catalogue_id.id,
                    'product_template_id': product_id,
                    'product_id': my_line.product_id.id,
                    'product_uom_qty': order_line_vals['product_uom_qty'],
                    'max_qty': my_line.qty_to_show,
                    'product_uom': my_line.product_tmpl_id.uom_id.id,
                    'name': my_line.product_tmpl_id.name,
                    # 'price_unit': 1,
                })]
                user_catalogue_id.write({'order_line': order_line})

            elif product_id != 0 and product_id in user_catalogue_id.order_line.mapped('product_template_id').ids:
                my_line = user_catalogue_id.order_line.filtered(
                    lambda item: item.product_template_id.id == product_id)
                my_line.sudo().write({'price_unit': order_line_vals['price_unit']})

            [line.sudo().write(catalogue_vals) if line.id == line_id else None for line in user_catalogue_id.order_line]

        lines = request.env['sale.order.line'].sudo().browse(catalogue_to_delete)
        if lines:
            lines.sudo().unlink()

    @http.route('/download/catalogue', type='http', auth="user", website=True, methods=['GET'], csrf=False)
    def print_catalogue(self, catalogue_id):
        user_catalogue_id = request.env['sale.order'].sudo().search(
            [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
        if user_catalogue_id:
            return user_catalogue_id.action_print_catalogue()
        else:
            return json.dumps([])

    @http.route('/my/request/quotation/form/<int:catalogue_id>', type='http', auth="user", website=True,
                methods=['GET'],
                csrf=False)
    def request_quotation(self, catalogue_id):
        print('============', catalogue_id)
        user_catalogue_id = request.env['sale.order'].sudo().search(
            [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
        if not user_catalogue_id:
            raise AccessDenied()
        rec_id = request.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1)
        user_id = request.env['res.users'].sudo().search(
            [('partner_id', '=', request.env.ref('base.partner_admin').id)])
        summary = _('Partner Quotation Request')
        note = _("Upgrade partner's Catalogue to Quotation")

        notification_ids = request.env['mail.activity'].sudo().search([
            ('activity_type_id', '=', 4),
            ('user_id', '=', user_id.id),
            ('res_model_id', '=', rec_id.id),
            ('res_id', '=', catalogue_id)
        ])
        notification_ids.sudo().unlink()

        request.env['mail.activity'].sudo().create({
            'activity_type_id': 4,
            'summary': summary,
            'user_id': user_id.id,
            'res_model_id': rec_id.id,
            'res_id': catalogue_id,
            'date_deadline': datetime.today(),
            'note': note,
        })

        # user_catalogue_id.sudo().write({'state': 'draft'})
        return request.redirect('/my/catalogue')

    @http.route('/my/request/sale/form/<int:catalogue_id>', type='http', auth="user", website=True, methods=['GET'],
                csrf=False)
    def request_sale(self, catalogue_id):
        user_catalogue_id = request.env['sale.order'].sudo().search(
            [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
        if not user_catalogue_id:
            raise AccessDenied()

        rec_id = request.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1)
        user_id = request.env['res.users'].sudo().search(
            [('partner_id', '=', request.env.ref('base.partner_admin').id)])
        summary = _('Partner Sale Order Request')
        note = _("Upgrade partner's Catalogue to Sale Order")

        notification_ids = request.env['mail.activity'].sudo().search([
            ('activity_type_id', '=', 4),
            ('user_id', '=', user_id.id),
            ('res_model_id', '=', rec_id.id),
            ('res_id', '=', catalogue_id)
        ])
        notification_ids.sudo().unlink()

        request.env['mail.activity'].sudo().create({
            'activity_type_id': 4,
            'summary': summary,
            'user_id': user_id.id,
            'res_model_id': rec_id.id,
            'res_id': catalogue_id,
            'date_deadline': datetime.today(),
            'note': note,
        })

        # user_catalogue_id.sudo().action_confirm()
        return request.redirect('/my/catalogue')

    @http.route('/website/catalogue/available/products', type='http', auth="user", website=True, methods=['GET'],
                csrf=False)
    def catalogue_available_products(self, catalogue_id, products):
        active_product_ids = products.translate({ord(i): None for i in '["]'}).split(',')
        user_catalogue_id = request.env['sale.order'].search([('id', '=', catalogue_id)])
        product_ids = user_catalogue_id.pricelist_id.item_ids.mapped('product_tmpl_id').filtered(
            lambda product_id: str(product_id.id) not in active_product_ids)
        if product_ids:
            response_data = [
                {
                    'product_id': line.product_tmpl_id.id,
                    'product_name': line.product_tmpl_id.name,
                    'max_qty': line.qty_to_show,
                    'price_unit': line.fixed_price,
                }
                for line in user_catalogue_id.pricelist_id.item_ids.filtered(
                    lambda line: line.product_tmpl_id in product_ids)
            ]
            return json.dumps(response_data)
        else:
            return json.dumps([])
