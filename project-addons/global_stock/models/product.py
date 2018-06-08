# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    global_stock = fields.Float(compute='_compute_global_stock')

    @api.multi
    def _compute_global_stock(self):
        for product in self:
            product_without_location = product.with_context(location=None)
            product.global_stock = product_without_location.sudo().virtual_stock_conservative
