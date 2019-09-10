# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MagentoBackend(models.Model):

    _inherit = 'magento.backend'

    @api.multi
    def force_update_product_stock_qty(self):
        mag_product_obj = self.env['magento.product.product']
        domain = self._domain_for_update_product_stock_qty()
        magento_products = mag_product_obj.search(domain)
        magento_products.write({'magento_qty': 0})
        magento_products.recompute_magento_qty()
        return True
