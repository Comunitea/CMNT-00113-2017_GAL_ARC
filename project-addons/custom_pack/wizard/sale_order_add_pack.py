# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleOrderAddPack(models.TransientModel):

    _name = 'sale.order.add.pack'
    product = fields.Many2one('product.product',
                              domain=[('is_pack', '=', True)], required=True)
    product_lines = fields.One2many('sale.order.add.pack.line', 'wizard')
    orig_sale_line = fields.Many2one('sale.order.line')
    qty = fields.Float()
    created = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderAddPack, self).default_get(fields_list)
        product_lines = []
        if self._context['active_model'] == 'sale.order.line':
            res['orig_sale_line'] = self._context['active_id']
            line = self.env['sale.order.line'].browse(
                self._context['active_id'])
            for child in line.pack_child_lines:
                product_lines.append(
                    (0, 0,
                     {'option': child.option.id,
                      'option_name': child.option.name,
                      'selected_product': child.product_id.id,
                      'selected_product_name': child.product_id.name,
                      'qty_available': child.product_id.qty_available,
                      'created_line_id': child.id}))
            res['product_lines'] = product_lines
            res['created'] = True
        return res

    @api.onchange('product')
    def product_change(self):
        if not self.product:
            return
        product_lines = []
        if self._context['active_model'] == 'sale.order':
            for pack_option in self.product.pack_options:
                product_lines.append((0, 0, {'option': pack_option.id}))
            self.product_lines = product_lines

    @api.multi
    def _create_line(self, product, qty, parent_line_id=None,
                     option=None, write_line=None):
        if not write_line:
            new_line = self.env['sale.order.line'].new({
                'product_id': product.id,
                'product_uom_qty': qty,
                'order_id': self._context.get('active_id'),
                'pack_parent_line': parent_line_id,
                'option': option,
            })
            new_line.product_id_change()
            line_vals = new_line._cache
            line_vals['product_uom_qty'] = qty
            new_line.product_uom_change()
            new_line._onchange_product_id_check_availability()
            if parent_line_id:
                line_vals['price_unit'] = 0.0
            return self.env['sale.order.line'].create(
                new_line._convert_to_write(line_vals))
        write_line.write({'product_uom_qty': qty})
        return write_line

    @api.multi
    def confirm(self):
        write_line = None
        if self._context['active_model'] == 'sale.order.line':
            write_line = self.env['sale.order.line'].browse(
                self._context['active_id'])
        super_line = self._create_line(
            self.product, self.qty, write_line=write_line)
        for line in self.product_lines:
            pack_product = self.env['product.pack.product'].search(
                [('option_id', '=', line.option.id),
                 ('product_id', '=', line.selected_product.id)])
            self._create_line(
                line.selected_product,
                self.qty * pack_product.qty_multiplier,
                parent_line_id=super_line.id,
                option=line.option,
                write_line=line.created_line_id)
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('qty')
    def qty_change(self):
        messages = [(x.selected_product.name, x._check_qty())
                    for x in self.product_lines.filtered(
                     lambda r: r.selected_product)]
        if messages:
            message_str = '\n'.join(
                ['{}: {}'.format(x[0], x[1]['warning']['message'])
                 for x in messages if 'warning' in x[1]])
            if message_str:
                return {'warning':
                        {'title': 'stock error',
                         'message': message_str}}


class SaleOrderAddPackLine(models.TransientModel):

    _name = 'sale.order.add.pack.line'

    wizard = fields.Many2one('sale.order.add.pack')
    option = fields.Many2one('product.pack.option', required=True)
    option_name = fields.Char(related='option.name')
    available_products = fields.One2many(
        'product.product', compute='_compute_available_products')
    selected_product = fields.Many2one('product.product', required=True)
    selected_product_name = fields.Char(related='selected_product.name',
                                        readonly=True)
    qty_available = fields.Float(
        related='selected_product.qty_available', readonly=True)
    created_line_id = fields.Many2one('sale.order.line')

    @api.depends('option')
    def _compute_available_products(self):
        for line in self:
            line.available_products = line.option.mapped('products.product_id')

    @api.onchange('selected_product')
    def product_change(self):
        return self._check_qty()

    @api.multi
    def _check_qty(self):
        if self._context['active_model'] == 'sale.order.line':
            order_id = self.env['sale.order.line'].browse(
                self._context['active_id']).order_id
        else:
            order_id = self._context['active_id']
        pack_product = self.env['product.pack.product'].search(
                [('option_id', '=', self.option.id),
                 ('product_id', '=', self.selected_product.id)])
        new_line = self.env['sale.order.line'].new({
            'product_id': self.selected_product.id,
            'product_uom_qty': self.wizard.qty * pack_product.qty_multiplier,
            'order_id': order_id,
        })
        new_line.product_id_change()
        new_line.product_uom_qty = self.wizard.qty * \
            pack_product.qty_multiplier
        return new_line._onchange_product_id_check_availability()
