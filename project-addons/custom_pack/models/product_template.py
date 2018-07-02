# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    pack_options = fields.One2many('product.pack.option', 'parent_product_id')
    is_pack = fields.Boolean(compute='_compute_is_pack', store=True)

    @api.depends('pack_options')
    def _compute_is_pack(self):
        for product in self:
            product.is_pack = len(product.pack_options)


class ProductBundleImporter(Component):

    _inherit = 'magento.product.bundle.importer'

    def run(self, binding, magento_record):
        pack_options = []
        for option in magento_record['extension_attributes']['bundle_product_options']:
            pack_option = {'name': option['title'], 'products': []}
            for product_data in option['product_links']:
                product = self.binder_for(
                    'magento.product.product').to_internal(
                        product_data['sku']).odoo_id
                pack_option['products'].append(
                    (0, 0, {'product_id': product.id,
                            'qty_multiplier': product_data['qty']}))
            pack_options.append((0, 0, pack_option))
        binding.odoo_id.pack_options.unlink()
        binding.odoo_id.write({'pack_options': pack_options})


class MagentoProductProduct(models.Model):
    _inherit = 'magento.product.product'

    @api.model
    def product_type_get(self):
        types = super(MagentoProductProduct, self).product_type_get()
        if 'bundle' not in [item[0] for item in types]:
            types.append(('bundle', 'Bundle'))
        return types
