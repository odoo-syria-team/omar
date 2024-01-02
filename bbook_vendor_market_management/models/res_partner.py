from odoo import models, fields, api


class PartnerInherit(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('none', 'None'),
        ('customer', 'Customer'),
        ('request_vendor', 'Pending Vendor'),
        ('vendor', 'Vendor'),
        ('request_super_vendor', 'Pending Vendor+'),
        ('super_vendor', 'Vendor+')], default="none", required=True, string="Partner Type")

    product_ids = fields.One2many('product.template', 'partner_id', string="Products")
    license_number = fields.Char(string="License Number")
    commercial_license = fields.Binary(string="Commercial License")
    authentication_of_signature = fields.Binary(string="Authentication of Signature")
    sponsor_license = fields.Binary(string="Sponsor's License")

    def action_make_vendor(self):
        for rec in self:
            rec.partner_type = 'vendor'
            template = self.env.ref('bbook_vendor_market_management.mail_template_partner_vendor')
            template.send_mail(rec.id)

            activity_id = self.env['mail.activity'].sudo().search([
                ('activity_type_id', '=', 4),
                ('user_id', '=', self.env.user.id),
                ('res_model_id', '=',
                 self.env['ir.model'].sudo().search([('model', '=', 'res.partner')], limit=1).id),
                ('res_id', '=', self.id)
            ])
            if activity_id:
                activity_id.action_done()

    def action_make_super_vendor(self):
        for rec in self:
            rec.partner_type = 'request_super_vendor'
            template = self.env.ref('bbook_vendor_market_management.mail_template_partner_super_vendor')
            template.send_mail(rec.id)

            activity_id = self.env['mail.activity'].sudo().search([
                ('activity_type_id', '=', 4),
                ('user_id', '=', self.env.user.id),
                ('res_model_id', '=',
                 self.env['ir.model'].sudo().search([('model', '=', 'res.partner')], limit=1).id),
                ('res_id', '=', self.id)
            ])
            if activity_id:
                activity_id.action_done()
