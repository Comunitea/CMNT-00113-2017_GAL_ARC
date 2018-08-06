# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    supplier_ref = fields.Char(compute='_compute_supplier_ref')
    supplier_name = fields.Char(compute='_compute_supplier_name')


    @api.depends('product_id', 'order_id.partner_id')
    def _compute_supplier_ref(self):
        for line in self:
            if not line.product_id:
                return
            partner_lang = line.product_id.with_context(
                lang=line.partner_id.lang,
                partner_id=line.partner_id.id)
            line.supplier_ref = partner_lang.code

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_supplier_name(self):
        for line in self:
            product_name = None
            if not line.product_id:
                return
            for supplier_info in line.product_id.seller_ids:
                if supplier_info.name.id == line.partner_id.id:
                    product_name = supplier_info.product_name or line.product_id.name
                    break
            line.supplier_name = product_name
