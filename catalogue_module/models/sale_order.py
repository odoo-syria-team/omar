from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('draft',), ('catalogue', 'Catalogue')], ondelete={'catalogue': 'set default'})

    def action_catalogue(self):
        for rec in self:
            rec.state = 'catalogue'

    def action_confirm_draft_catalogue(self):
        for rec in self:
            rec.state = 'draft'

    def action_print_catalogue(self):
        for rec in self:
            action = self.env.ref('catalogue_module.catalogue_sale_order_report').report_action(rec)
            return action
