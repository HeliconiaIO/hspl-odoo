# -*- encoding :utf-8 -*-
from odoo import models, fields, api


class ProductProductReport(models.TransientModel):
    _name = "product.product.report"

    @api.multi
    def get_products(self):
        products_mailing = []
        cur_recs = self.env["product.product"].search([('last_move_date', '!=', False)])
        # print("dddd", cur_recs)
        for cur_rec in cur_recs:
            if cur_rec.categ_id.limit_days < cur_rec.move_days:
                products_mailing.append(cur_rec)
        return products_mailing

    @api.multi
    def get_users(self):
        users_mailing = []
        cur_users = self.env["res.users"].search([('email', '!=', False)])
        print("users", cur_users)
        for rec in cur_users:
            print(rec.email)
            users_mailing.append(rec.email,)
        print("USER_LIST", users_mailing)
        myString = ",".join(users_mailing)
        print("MY St", myString)

        return myString


class StockMovement(models.TransientModel):

    _name = "stock.wizard"

    from_date = fields.Datetime(string="From  Date", required="True")
    to_date = fields.Datetime(string="To  Date", required="True")

    @api.multi
    def generate_report(self):

        non_move_product_list = []

        product_recs = self.env["product.product"].search([('last_move_date', '!=', False)])
        print(product_recs)
        for rec in product_recs:
            print(self.from_date, rec.last_move_date)
            print(self.to_date, rec.last_move_date)
            if self.to_date > rec.last_move_date > self.from_date:
                non_move_product_list.append(rec.id)
                print("Last Move Product's Id's===>>>", non_move_product_list)

        tree_view_ref = self.env.ref('stock_movement.stock_movement_tree_view')

        return {
            'name': "Stock Movement",
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', non_move_product_list)],
            # 'domain': "[('last_move_date', 'not in', False)]",
            'views': [(tree_view_ref and tree_view_ref.id or False, 'tree')],
        }


