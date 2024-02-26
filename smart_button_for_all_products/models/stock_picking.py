from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.move.line'

    
    product_price = fields.Float(compute='_compute_product_price', string='Product Price' ,store=True)
    product_total_price = fields.Float(compute='_compute_product_price', string='Product Total Price' ,store=True)

    @api.depends('product_id')
    def _compute_product_price(self):
        for picking in self:
            if picking.move_id.sale_line_id and picking.product_id:
                sale_order_line = picking.move_id.sale_line_id.filtered(
                    lambda line: line.product_id == picking.product_id
                )
                if sale_order_line:
                    picking.product_price = sale_order_line[0].price_unit
                    picking.product_total_price = picking.product_price * picking.qty_done




class StockMove(models.Model):
    _inherit = 'stock.move'

    product_price = fields.Float(string='Product Price', compute='_compute_product_price', readonly=True)

    @api.depends('sale_line_id')
    def _compute_product_price(self):
        for move in self:
            if move.sale_line_id:
                move.product_price = move.sale_line_id.price_unit
            else:
                move.product_price = 0.0