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
    @http.route('/my/catalogue/<int:catalogue_id>', auth="user", csrf=False, website=True,
                methods=['GET'])
    def get_product_record(self, catalogue_id, **post):
        try:
            user_catalogue_id = request.env['sale.order'].sudo().search(
                [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
            if not user_catalogue_id:
                raise AccessDenied()

        except UserError as e:
            return str(e)
        except Exception as e:
            return str(e)

        # if request.httprequest.method == 'POST':
        #     try:
        #         data = self._write_vals()
        #
        #         if catalogue_id == -1:
        #             user_product_id = request.env['sale.order'].sudo().create(
        #                 {
        #                     'name': data['name'],
        #                     'partner_id': request.env.user.partner_id.id,
        #                     'company_id': request.env.user.company_id.id,
        #                     'product_state': 'approved' if request.env.user.partner_id.partner_type == 'super_vendor' else 'pending'
        #                 })
        #
        #             if request.env.user.partner_id.partner_type == 'vendor':
        #                 summary = _('New Product Request for %s', request.env.user.partner_id.name)
        #                 note = _('%s is waiting his request to add new product to be approved',
        #                          request.env.user.partner_id.name)
        #             else:
        #                 summary = _('Added product by %s', request.env.user.partner_id.name)
        #                 note = _('%s has just added new product', request.env.user.partner_id.name)
        #
        #             self.send_notification_to_admin(user_product_id, note, summary)
        #
        #         else:
        #             if not user_catalogue_id:
        #                 raise AccessDenied()
        #
        #             summary = _('Product has been edited by %s', request.env.user.partner_id.name)
        #             note = _('%s has just edited %s product', request.env.user.partner_id.name, data['name'])
        #             self.delete_older_notification(user_catalogue_id)
        #             self.send_notification_to_admin(user_catalogue_id, note, summary)
        #
        #         user_product_id.sudo().write(data)
        #
        #         return request.redirect('/my/products')
        #
        #     except UserError as e:
        #         return str(e)
        #     except Exception as e:
        #         return str(e)

        if request.httprequest.method == 'GET':
            try:
                if catalogue_id != -1 and catalogue_id not in user_catalogue_id.ids:
                    raise AccessDenied()

                return request.render('catalogue_module.catalogue_form', {
                    'user_id': request.env.user,
                    'page_name': 'catalogue_form_page',
                    'o': user_catalogue_id,
                })
            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

    def _write_vals(self):

        form_dict = {}
        form_file_dict = {}
        products_vals = {}

        form = request.httprequest.form

        for key, value in zip(form.keys(), form.values()):
            form_dict[key] = form.getlist(key)

        form_files = request.httprequest.files
        for key, value in zip(form_files.keys(), form_files.values()):
            form_file_dict[key] = form_files.getlist(key)

        for key, value in zip(form_file_dict.keys(), form_file_dict.values()):
            if key == 'product_image':
                image_data = value[0].read()
                if len(image_data) > 0 or form_dict['product_image_text'][0] == "deleted":
                    products_vals['image_1920'] = base64.b64encode(image_data)

        for key, value in zip(form_dict.keys(), form_dict.values()):

            if key == 'list_price':
                products_vals[key] = float(value[0]) if value else 1.0

            if key in ['name', 'description', 'barcode', 'default_code']:
                products_vals[key] = value[0]

        products_vals['sale_ok'] = True
        products_vals['purchase_ok'] = False
        products_vals['detailed_type'] = 'product'
        products_vals['product_state'] = 'pending'
        products_vals['categ_id'] = request.env.ref('product.product_category_1').id

        return products_vals

        # products_variant_vals = {}
        # products_specification_vals = {}
        # elif key.startswith('selected_value_ids_'):
        #     variant_id = int(key.split('_')[3])
        #     products_variant_vals.setdefault(variant_id, []).extend([int(val) for val in value])
        #
        # elif key.startswith('selected_specification_value_'):
        #     specification_id = int(key.split('_')[3])
        #     products_specification_vals[specification_id] = value[0]

        # attribute_line_ids_updates = [(1, variant_id, {'value_ids': [(6, 0, value_ids)]}) for variant_id, value_ids in
        #                               products_variant_vals.items()]
        # specification_ids_updates = [(1, specification_id, {'value': value}) for specification_id, value in
        #                              products_specification_vals.items()]

        # products_vals["attribute_line_ids"] = attribute_line_ids_updates
        # products_vals["specification_ids"] = specification_ids_updates

        # print("products_vals----------------------------------", products_vals)

    @http.route('/download/catalogue', type='http', auth="user", website=True, methods=['GET'], csrf=False)
    def print_catalogue(self, catalogue_id):
        print('=================', catalogue_id)
        user_catalogue_id = request.env['sale.order'].sudo().search(
                [('id', '=', catalogue_id), ('partner_id', '=', request.env.user.partner_id.id)])
        if user_catalogue_id:
            return user_catalogue_id.action_print_catalogue()
        else:
            return json.dumps([])


