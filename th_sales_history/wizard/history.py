# -*- coding: utf-8 -*-
# Part of Tech Heliconia. See LICENSE file for copyright and licensing details.

from openerp import models, fields, api


class SaleLineHistory(models.TransientModel):

    _name = 'sale.line.history'

    select = fields.Boolean('Select')
    line_id = fields.Many2one('sale.order.line', 'Order Line')
    product_id = fields.Many2one('product.product', "Product")
    order_id = fields.Many2one('sale.order', "Order")
    s_date = fields.Date("Sold Date")
    s_qty = fields.Float("Past Qty")
    s_unit_price = fields.Float('Past Unit Price')
    s_subtotal = fields.Float('Past Subtotal')
    c_qty = fields.Float("Current Qty")
    c_unit_price = fields.Float('Current Price')
    c_subtotal = fields.Float('Current Subtotal')
    history_id = fields.Many2one('sale.history', 'History')

    @api.onchange('c_qty', 'c_unit_price')
    def onchange_current_qty(self):
        if self.c_qty and self.c_unit_price:
            self.c_subtotal = self.c_qty * self.c_unit_price


class SalesHistory(models.TransientModel):

    _name = 'sale.history'

    @api.multi
    def get_default_model(self):
        model_id = self.env['ir.model'].search(
            [('model', '=', self._context.get('active_model'))], limit=1)
        if model_id:
            return model_id

    @api.multi
    def get_default_order(self):
        if self._context and \
                self._context.get('active_model') == 'sale.order' and \
                self._context.get('active_id'):
            return self._context.get('active_id')

    model_id = fields.Many2one('ir.model', 'Model', default=get_default_model)
    order_id = fields.Many2one(
        'sale.order', 'Sale Order', default=get_default_order)
    history_ids = fields.One2many('sale.line.history', 'history_id', 'History')

    @api.multi
    def add_products(self):

        line_env = self.env['sale.order.line']
        for line in self.history_ids:
            if line.select:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.c_qty,
                    'product_uom': line.line_id.product_uom.id,
                    'order_id': self.order_id.id
                }
                line_env.create(line_vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
