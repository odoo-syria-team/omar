from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    partner_id = fields.Many2one('res.partner', string='Partner')
    product_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved')], default="draft", required=True, string="Status")

    @api.model
    def create(self, vals):
        res = super(ProductTemplateInherit, self).create(vals)
        if self.env.user.has_group('base.group_partner_manager'):
            res['product_state'] = 'approved'
        return res

    def approve_product(self):
        for rec in self:
            if rec.product_state == 'pending':
                rec.product_state = 'approved'
                template = self.env.ref('bbook_vendor_market_management.mail_template_product_approve')
                template.send_mail(rec.id)

                activity_id = self.env['mail.activity'].sudo().search([
                    ('activity_type_id', '=', 4),
                    ('user_id', '=', self.env.user.id),
                    ('res_model_id', '=',
                     self.env['ir.model'].sudo().search([('model', '=', 'product.template')], limit=1).id),
                    ('res_id', '=', self.id)
                ])
                if activity_id:
                    activity_id.action_done()
