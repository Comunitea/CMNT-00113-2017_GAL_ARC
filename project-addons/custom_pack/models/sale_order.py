# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    pack_parent_line = fields.Many2one('sale.order.line', ondelete='cascade')
    pack_child_lines = fields.One2many(
        'sale.order.line', 'pack_parent_line')
    pack_line = fields.Boolean(compute='_compute_is_pack_line')
    option = fields.Many2one('product.pack.option')

    @api.depends('pack_parent_line', 'pack_child_lines')
    def _compute_is_pack_line(self):
        for line in self:
            if line.pack_parent_line or line.pack_child_lines:
                line.pack_line = True
            else:
                line.pack_line = False


class SaleOrderImporter(Component):
    _inherit = 'magento.sale.order.importer'

    def _merge_sub_items(self, product_type, top_item, child_items):
        super(SaleOrderImporter, self)._merge_sub_items(
            product_type, top_item, child_items)
        if child_items and product_type=='bundle':
            for child_item in child_items:
                child_item['child_lines'] = []
            top_item['child_lines'] = child_items
        else:
            top_item['child_lines'] = []
        return top_item


class SaleOrderLineImportMapper(Component):

    _inherit = 'magento.sale.order.line.mapper'

    children = [('child_lines', 'bundle_line_ids', 'magento.sale.order.line'),
                ]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        if map_record.source.get(from_attr):
            return super(SaleOrderLineImportMapper, self)._map_child(
                map_record, from_attr, to_attr, model_name)

class MagentoSaleOrderLine(models.Model):

    _inherit = 'magento.sale.order.line'

    bundle_line_ids = fields.One2many(
        comodel_name='magento.sale.order.line',
        inverse_name='top_line_id',
        string='bundle Lines'
    )

    top_line_id = fields.Many2one('magento.sale.order.line')

    @api.model
    def create(self, vals):
        top_line_id = vals.get('top_line_id')
        if top_line_id:
            binding = self.env['magento.sale.order.line'].browse(top_line_id)
            vals['pack_parent_line'] = binding.odoo_id.id
            vals['magento_order_id'] = binding.magento_order_id.id
        return super(MagentoSaleOrderLine, self).create(vals)
