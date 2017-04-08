# -*- coding: utf-8 -*-
# Part of Tech Heliconia. See LICENSE file for copyright and licensing details.
from openerp import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def open_sale_history(self):
        context = self._context.copy()
        history_form = self.env.ref(
            'th_sales_history.th_sale_history_form', False)
        past_order = self.search(
            [('partner_id', '=', self.partner_id.id),
             ('state', 'in', ['done', 'sale'])])
        history_list = []
        for order in past_order:
            for line in order.order_line:
                history_val = {
                    "product_id": line.product_id.id,
                    "order_id": line.order_id.id,
                    "s_date": line.order_id.date_order,
                    "s_qty": line.product_uom_qty,
                    "s_unit_price": line.price_unit,
                    "s_subtotal": line.price_subtotal,
                    "c_qty": line.product_uom_qty,
                    "c_unit_price": line.price_unit,
                    "c_subtotal": line.price_subtotal,
                    "line_id": line.id,
                }
                history_list.append((0, 0, history_val))
        context.update({'default_history_ids': history_list})
        return {
            'name': _('Sales History'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.history',
            'views': [(history_form.id, 'form')],
            'view_id': history_form.id,
            'context': context,
            'target': 'new',
        }

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        self.order_count = self.search_count(
            [('partner_id', '=', self.partner_id.id),
             ('state', 'in', ['done', 'sale'])])

    order_count = fields.Integer('Order Count')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
