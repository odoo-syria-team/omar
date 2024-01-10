# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .log import logger


class SaleOrder(models.Model):
    _inherit = "res.company"

    test = fields.Boolean('test', compute="teeeest")

    def teeeest(self):
        for rec in self:
            rec.test = False
            account_move_lines = self.env['account.move.line'].search([('company_id', '=', rec.id)])

            logger.debug(account_move_lines)
            for re in account_move_lines:
                re.company_currency_id = None
