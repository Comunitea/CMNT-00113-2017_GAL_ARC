# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductPackProduct(models.Model):

    _name = 'product.pack.product'

    option_id = fields.Many2one('product.pack.option', ondelete="cascade")
    product_id = fields.Many2one('product.product', required=True)
    qty_multiplier = fields.Float(default=1)
