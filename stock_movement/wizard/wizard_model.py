# -*- encoding :utf-8 -*-
from odoo import models, fields, api


class ProductProductReport(models.TransientModel):
    _name = "product.product.report"

    sent_alert = fields.Selection([
        ('globally', 'Globally'),
        ('category_wise', 'Category Wise'),
        ('warehouse_wise', 'Warehouse Wise')
    ], string="Sent Alert")
    current_category_id = fields.Many2one("product.category")
    current_warehouse_id = fields.Many2one("stock.warehouse")

    @api.multi
    def get_products(self):
        products_mailing = []
        if self.sent_alert == 'globally':
            cur_recs = self.env["product.product"].search([('last_move_date', '!=', False)])
            # print("dddd", cur_recs)
            for cur_rec in cur_recs:
                if cur_rec.categ_id.limit_days < cur_rec.move_days:
                    products_mailing.append(cur_rec)
        if self.sent_alert == 'category_wise':
            cur_recs = self.env["product.product"].search([
                ('last_move_date', '!=', False),
                ('categ_id', '=', self.current_category_id.id)])
            # print("dddd", cur_recs)
            for cur_rec in cur_recs:
                if cur_rec.categ_id.limit_days < cur_rec.move_days:
                    products_mailing.append(cur_rec)
        if self.sent_alert == 'warehouse_wise':
            product_obj = self.env["product.product"]
            product_ids = set()
            domain_quant = product_obj.with_context(warehouse=self.current_warehouse_id.id)._get_domain_locations()[0]
            quants_groupby = self.env['stock.quant'].read_group(
                domain_quant, ['product_id'], ['product_id'], orderby='id')
            for quant in quants_groupby:
                product_ids.add(quant['product_id'][0])
            product_ids = list(product_ids)
            cur_recs = product_obj.search([
                ('last_move_date', '!=', False),
                ('id', 'in', product_ids)])
            for cur_rec in cur_recs:
                if self.current_warehouse_id.limit_days < cur_rec.move_days:
                    products_mailing.append(cur_rec)
        return products_mailing

    @api.multi
    def get_users(self):
        res = False
        if self.sent_alert == 'globally':
            res = ",".join([user.email for user in self.env.user.company_id.alert_user])
            # cur_users = self.env["res.users"].search([('email', '!=', False)])
            # print("users", cur_users)
            # for rec in cur_users:
            #     print(rec.email)
            #     users_mailing.append(rec.email)
            # print("USER_LIST", users_mailing)
            # myString = ",".join(users_mailing)
            # print("MY St", myString)
        if self.sent_alert == 'category_wise':
            res = ",".join([user.email for user in self.current_category_id.alert_user])
        if self.sent_alert == 'warehouse_wise':
            res = ",".join([user.email for user in self.current_warehouse_id.alert_user])
        return res


class StockMovement(models.TransientModel):

    _name = "stock.wizard"

    from_date = fields.Datetime(string="From  Date")
    to_date = fields.Datetime(string="To  Date")
    current_category_id = fields.Many2many("product.category")
    current_warehouse_id = fields.Many2many("stock.warehouse")
    cate_ware_selection = fields.Selection([
        ('globally', 'Globally'),
        ('category', 'Category Wise'),
        ('warehouse', 'Warehouse Wise')], default='globally', string="Selection")
    days = fields.Integer(string="Enter Days....")

    @api.multi
    def generate_report(self):

        category_ids = []
        warehouse_ids = []

        for cur_category_id in self.current_category_id:
            # print("Category Id", cur_category_id.id)
            category_ids.append(cur_category_id.id)

        for cur_warehouse_id in self.current_warehouse_id:
            # print("Warehouse Id", cur_warehouse_id.id)
            warehouse_ids.append(cur_warehouse_id.id)

        # print("!@#", category_ids)
        # print("(*&", warehouse_ids)

        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'days': self.days,
            'current_category_id': category_ids,
            'current_warehouse_id': warehouse_ids,
            'cate_ware_selection' : self.cate_ware_selection
        }

        print("data", data)
        return self.env['report'].with_context(portrait=True).get_action(
            self, 'stock_movement.slow_moving_product_report', data=data)




       # return Tree view..
        # product_recs = self.env["product.product"].search([('last_move_date', '!=', False)])
        # # print(product_recs)
        # for rec in product_recs:
        #     # print(self.from_date, rec.last_move_date)
        #     # print(self.to_date, rec.last_move_date)
        #     if self.to_date > rec.last_move_date > self.from_date:
        #         print("dd", rec.id)

        # data = self.pre_print_report(data)
        # data['form'].update({'sort_selection': self.sort_selection})
        # return self.env['report'].with_context(landscape=True).get_action(self, 'account.report_journal', data=data)

        # non_move_product_list = []
        #
        # product_recs = self.env["product.product"].search([('last_move_date', '!=', False)])
        # print(product_recs)
        # for rec in product_recs:
        #     print(self.from_date, rec.last_move_date)
        #     print(self.to_date, rec.last_move_date)
        #     if self.to_date > rec.last_move_date > self.from_date:
        #         non_move_product_list.append(rec.id)
        #         print("Last Move Product's Id's===>>>", non_move_product_list)
        #
        # tree_view_ref = self.env.ref('stock_movement.stock_movement_tree_view')

        # return {
        #     'name': "Stock Movement",
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'product.product',
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        #     'domain': [('id', 'in', non_move_product_list)],
        #     # 'domain': "[('last_move_date', 'not in', False)]",
        #     'views': [(tree_view_ref and tree_view_ref.id or False, 'tree')],
        # }
        #

