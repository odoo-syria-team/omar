from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.portal.controllers.portal import pager
from odoo.addons.portal.controllers import portal
import base64
from datetime import datetime


# product list view
class ProductTemplate(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(ProductTemplate, self)._prepare_home_portal_values(counters)
        values['product_count'] = request.env['product.template'].search_count(
            [('partner_id', '=', request.env.user.partner_id.id)])
        return values

    @http.route(['/my/products', '/my/products/page/<int:page>'], auth="user", csrf=False, website=True,
                methods=['GET'])
    def get_products(self, sortby='name', page=1, search='', search_in='Product'):

        try:
            if request.env.user.partner_id.partner_type not in ['vendor', 'super_vendor']:
                raise AccessDenied()

            sorted_list = {
                'id': {'label': 'Latest', 'order': 'id desc'},
                'name': {'label': 'Product', 'order': 'name'},
                'default_code': {'label': 'Internal Reference', 'order': 'default_code'},
            }
            default_order_by = sorted_list[sortby]['order']
            search_list = {
                'Product':
                    {
                        'label': 'Product',
                        'input': 'Product',
                        'domain': [('name', 'ilike', search), ('partner_id', '=', request.env.user.partner_id.id)]
                    },
                'Internal Reference':
                    {
                        'label': 'Internal Reference',
                        'input': 'Internal Reference',
                        'domain': [('Internal Reference', 'ilike', search),
                                   ('partner_id', '=', request.env.user.partner_id.id)]
                    },
            }
            search_domain = search_list[search_in]['domain']

            total_product_ids = http.request.env['product.template'].sudo().search_count(search_domain)

            page_details = pager(url='/my/products',
                                 total=total_product_ids,
                                 page=page,
                                 url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
                                 step=10
                                 )
            product_ids = http.request.env['product.template'].sudo().search(search_domain,
                                                                             limit=10, order=default_order_by,
                                                                             offset=page_details['offset'])
            if not product_ids:
                return request.redirect('/my/home')
            return request.render('bbook_vendor_market_management.product_list', {
                'user_id': request.env.user,
                'page_name': 'product_list_page',
                'product_ids': product_ids,
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

    # product form view
    @http.route('/my/products/<int:product_id>', auth="user", csrf=False, website=True,
                methods=['GET', 'POST'])
    def get_product_record(self, product_id, **post):
        try:
            if request.env.user.partner_id.partner_type not in ['vendor', 'super_vendor']:
                raise AccessDenied()

        except UserError as e:
            return str(e)
        except Exception as e:
            return str(e)

        user_product_id = request.env['product.template'].sudo().search(
            [('id', '=', product_id), ('partner_id', '=', request.env.user.partner_id.id)])
        if request.httprequest.method == 'POST':
            try:
                if 'delete_ok' in request.httprequest.form.keys():
                    user_product_id.sudo().unlink()
                    return request.redirect('/my/products')

                data = self._write_vals()

                if product_id == -1:
                    user_product_id = request.env['product.template'].sudo().create(
                        {
                            'name': data['name'],
                            'partner_id': request.env.user.partner_id.id,
                            'company_id': request.env.user.company_id.id,
                            'product_state': 'approved' if request.env.user.partner_id.partner_type == 'super_vendor' else 'pending'
                        })

                    if request.env.user.partner_id.partner_type == 'vendor':
                        summary = _('New Product Request for %s', request.env.user.partner_id.name)
                        note = _('%s is waiting his request to add new product to be approved', request.env.user.partner_id.name)
                    else:
                        summary = _('Added product by %s', request.env.user.partner_id.name)
                        note = _('%s has just added new product', request.env.user.partner_id.name)

                    self.send_notification_to_admin(user_product_id, note, summary)

                else:
                    if not user_product_id:
                        raise AccessDenied()

                    summary = _('Product has been edited by %s', request.env.user.partner_id.name)
                    note = _('%s has just edited %s product', request.env.user.partner_id.name, data['name'])
                    self.delete_older_notification(user_product_id)
                    self.send_notification_to_admin(user_product_id, note, summary)

                user_product_id.sudo().write(data)

                return request.redirect('/my/products')

            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

        else:
            try:
                if product_id != -1 and product_id not in user_product_id.ids:
                    raise AccessDenied()

                return request.render('bbook_vendor_market_management.product_form', {
                    'user_id': request.env.user,
                    'page_name': 'product_form_page',
                    'product_id': user_product_id,
                })
            except UserError as e:
                return str(e)
            except Exception as e:
                return str(e)

    def delete_older_notification(self, user_product_id):
        rec_id = request.env['ir.model'].sudo().search([('model', '=', 'product.template')], limit=1)
        user_id = request.env['res.users'].sudo().search(
            [('partner_id', '=', request.env.ref('base.partner_admin').id)])
        notification_ids = request.env['mail.activity'].sudo().search([
            ('activity_type_id', '=', 4),
            ('user_id', '=', user_id.id),
            ('res_model_id', '=', rec_id.id),
            ('res_id', '=', user_product_id.id)
        ])
        notification_ids.sudo().unlink()

    def send_notification_to_admin(self, user_product_id, note, summary):
        rec_id = request.env['ir.model'].sudo().search([('model', '=', 'product.template')], limit=1)
        user_id = request.env['res.users'].sudo().search(
            [('partner_id', '=', request.env.ref('base.partner_admin').id)])

        request.env['mail.activity'].sudo().create({
            'activity_type_id': 4,
            'summary': summary,
            'user_id': user_id.id,
            'res_model_id': rec_id.id,
            'res_id': user_product_id.id,
            'date_deadline': datetime.today(),
            'note': note,
        })

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
