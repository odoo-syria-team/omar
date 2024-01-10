# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "res.company"

    test = fields.Boolean('test', compute="teeeest")

    def teeeest(self):
        for rec in self:
            rec.test = False
            account_move_lines = self.env['account.move.line'].search([('company_id', '=', rec.id)])
            account_move_lines.company_currency_id = None
