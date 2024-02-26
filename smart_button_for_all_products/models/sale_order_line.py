from odoo import models, fields, api,_

class ResPartner(models.Model):
    _inherit = 'sale.order.line'


    product_max_quantity = fields.Integer('Max Quantity' )
class ResPartner(models.Model):
    _inherit = 'sale.order'

    transfer_ids = fields.Many2many('stock.picking', string='Transfers', compute='_compute_transfer_ids' , store=True)

    
    ds = fields.Boolean('', compute='get_max_quantity' , store=True)

    def _compute_transfer_ids(self):
        for order in self:
            order.transfer_ids = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            
    @api.depends('order_line')
    def get_max_quantity(self):
        for order in self:
            for line in order.order_line:
                pricelist = order.pricelist_id
                if pricelist:
                    pricelist_item = pricelist.item_ids.filtered(lambda item: item.product_tmpl_id.id == line.product_id.product_tmpl_id.id)
                    if pricelist_item:
                        line.product_max_quantity = pricelist_item[0].max_quant
                    else:
                        line.product_max_quantity = 0
                else:
                    line.product_max_quantity = 0

            order.ds = False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.user_ids.filtered(lambda user: user.login == 'portal'):
            warehouse = self.env['stock.warehouse'].search([('code', '=', 'Port')], limit=1)
            if warehouse:
                self.warehouse_id = warehouse

class ProductPricelistLine(models.Model):
    _inherit = 'product.pricelist.item'
    _description = "this module is for product.pricelist"



    max_quant = fields.Integer('Max Quantity')