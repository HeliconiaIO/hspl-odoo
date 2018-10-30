# -*- encoding :utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class THReporting_Qweb(models.AbstractModel):

    _name = 'report.stock_movement.slow_moving_product_report'

    @api.model
    def render_html(self, docids, data=None):
        prod_domain = []
        print "Render Data\n\n\n", data
        from_date = data.get("from_date", False)
        to_date = data.get("to_date", False)
        if from_date:
            prod_domain += [('last_move_date', '>', from_date)]
        if to_date:
            prod_domain += [('last_move_date', '<', to_date)]
        days = data.get("days", False)
        if days:
            prod_domain += [('move_days', '>=', days)]
        print "domain", prod_domain

        if data.get("cate_ware_selection") == 'globally':
            products = self.env['product.product'].search(prod_domain)

        product_ids = [product.id for product in products]

        # """TODO : first fetch product.product , product.category and warehouse"""

        doc_args = {
            'doc_ids': product_ids,
            'doc_model': self.env['product.product'],
            'data': data,
            'docs': self.env['product.product'].browse(product_ids),
        }
        return self.env['report'].render('stock_movement.slow_moving_product_report', doc_args)
