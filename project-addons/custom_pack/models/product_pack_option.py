# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProductPackOption(models.Model):

    _name = 'product.pack.option'

    name = fields.Char(required=True)
    parent_product_id = fields.Many2one('product.template', 'Parent product')
    products = fields.One2many('product.pack.product', 'option_id')
