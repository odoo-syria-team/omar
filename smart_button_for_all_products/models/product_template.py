
from odoo import models, fields, api,_

class ResPartner(models.Model):
    _inherit = 'product.template'

    dimension = fields.Integer('Dimension' )



