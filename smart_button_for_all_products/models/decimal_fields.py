from odoo import models, fields , api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float('Price', digits=(16, 8))
    standard_price = fields.Float('Standear Price', digits=(16, 8))
    volume = fields.Float('Volume', digits=(16, 8))

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     price_unit = fields.Float('Unit Price', digits=(16, 8))
#     discount = fields.Float('Discount', digits=(16, 8))
#     product_uom_qty = fields.Float('Quantity', digits=(16, 8))
#     qty_delivered = fields.Float('Delivered', digits=(16, 8))
#     price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', digits=(16, 8))
#     price_tax = fields.Float(string='Tax', compute='_compute_amount', digits=(16, 8))
#     price_total = fields.Float(string='Total', compute='_compute_amount', digits=(16, 8))

#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
#             totals = list(tax_results['totals'].values())[0]
#             amount_untaxed = totals['amount_untaxed']
#             amount_tax = totals['amount_tax']

#             line.update({
#                 'price_subtotal': amount_untaxed,
#                 'price_tax': amount_tax,
#                 'price_total': amount_untaxed + amount_tax,
#             })

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total = fields.Monetary('Total Amount', digits=(16, 8))
    amount_residual = fields.Monetary('Residual Amount', digits=(16, 8))

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    debit = fields.Monetary('Debit', digits=(16, 8))
    discount = fields.Float('Discount', digits=(16, 8))
    credit = fields.Monetary('Credit', digits=(16, 8))
    balance = fields.Monetary('Balance', digits=(16, 8))
    price_subtotal = fields.Monetary('Sub total', digits=(16, 8))
    price_total =  fields.Monetary('Total', digits=(16, 8))