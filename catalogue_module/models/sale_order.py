from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('draft',), ('catalogue', 'Catalogue')], ondelete={'catalogue': 'set default'})

    def action_catalogue(self):
        for rec in self:
            rec.state = 'catalogue'

    def action_confirm_draft_catalogue(self):
        for rec in self:
            rec.state = 'draft'
            activity_id = self.env['mail.activity'].sudo().search([
                ('activity_type_id', '=', 4),
                ('user_id', '=', self.env.user.id),
                ('res_model_id', '=',
                 self.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1).id),
                ('res_id', '=', self.id)
            ])
            if activity_id:
                activity_id.action_done()

    def action_print_catalogue(self):
        for rec in self:
            action = self.env.ref('catalogue_module.catalogue_sale_order_report').report_action(rec)
            return action

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        for rec in self:
            rec.state = 'draft'
            activity_id = self.env['mail.activity'].sudo().search([
                ('activity_type_id', '=', 4),
                ('user_id', '=', self.env.user.id),
                ('res_model_id', '=',
                 self.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1).id),
                ('res_id', '=', self.id)
            ])
            if activity_id:
                activity_id.action_done()
        return res


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    max_qty = fields.Float('Available Quantity')

