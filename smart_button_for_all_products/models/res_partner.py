from odoo import models, fields, api,_

class ResPartner(models.Model):
    _inherit = 'res.partner'

    counter_products = fields.Integer('products' , compute="_compute_product_count")


    def _compute_product_count(self):
        for rec in self:
            orders = self.env['sale.order'].search([('partner_id' , '=' , self.id)])
            if orders :
                orders = orders.mapped('order_line')
                
            rec.counter_products = len(orders)

    def open_sale_order_products(self):
        orders = self.env['sale.order'].search([('partner_id' , '=' , self.id)])
        if orders :
            orders = orders.mapped('order_line')

        
        action = {
            'res_model': 'sale.order.line',
            'type': 'ir.actions.act_window'
        }
        
       
        action.update({
            'name': _("products"),
            'domain': [('id', 'in', orders.ids)],
            'view_mode': 'tree'
        })
        return action
