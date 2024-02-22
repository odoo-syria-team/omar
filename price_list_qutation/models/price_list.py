from odoo import models,api, fields,_



class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    _description = "this module is for product.pricelist"
    partner_id = fields.Many2one('res.partner' , string = 'Partner' ,required=True)
    def create_quotation(self):
        selected_items = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.id), ('to_select', '!=', False)])
        
        if selected_items:
            quotation_vals = {
                'state': 'draft',
                'partner_id': self.partner_id.id,  # Set the partner for the new quotation
                # Add more fields as needed
            }
            
            quotation = self.env['sale.order'].create(quotation_vals)
            
            for item in selected_items:
                # Create the quotation line based on the product.pricelist.item data
                line_vals = {
                    'order_id': quotation.id,
                    'product_template_id': item.product_tmpl_id.id,
                    'product_id': item.product_id.id,
                    'price_unit': item.fixed_price,
                    'product_uom_qty': item.qty_to_show,
                    'product_uom': item.product_tmpl_id.uom_id.id,
                    'name': item.product_tmpl_id.name,
                    # Add more fields as needed
                }
                
                self.env['sale.order.line'].create(line_vals)
            
            # Do any additional operations or actions needed
            # e.g., open the created quotation or show a success message
        else:
            # Handle the case when no items are selected
            pass



class ProductPricelistLine(models.Model):
    _inherit = 'product.pricelist.item'
    _description = "this module is for product.pricelist"

    to_select = fields.Boolean(' ')
    qty_on_hand = fields.Float(string="Quantity on Hand", related="product_tmpl_id.qty_available", readonly=True)
    qty_to_show = fields.Float(string="Quantity to Show")





