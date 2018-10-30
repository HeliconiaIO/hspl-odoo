
from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as df


class ThResCompany(models.Model):

    _inherit = "res.company"

    sent_alert = fields.Selection([
        ('globally', 'Globally'),
        ('category_wise', 'Category Wise'),
        ('warehouse_wise', 'Warehouse Wise')
    ])

    limit_days = fields.Integer("Limits Days")

    alert_user = fields.Many2many('res.users', string="Select User", create=False)


class THStockConfigSettings(models.TransientModel):

    _inherit = "stock.config.settings"

    @api.model
    def get_default_sent_alert(self, fields):
        # don't forward-port in v11.0, the API of config wizards changed.
        # digits = self.env.ref('product.decimal_stock_weight').digits
        return {'sent_alert': self.env.user.company_id.sent_alert}

    @api.multi
    def set_sent_alert(self):
        # don't forward-port in v11.0, the API of config wizards changed.
        self.company_id.sent_alert = self.sent_alert

    @api.model
    def get_default_limit_days(self, fields):
        # don't forward-port in v11.0, the API of config wizards changed.
        # digits = self.env.ref('product.decimal_stock_weight').digits
        return {'limit_days': self.env.user.company_id.limit_days}

    @api.multi
    def set_limit_days(self):
        # don't forward-port in v11.0, the API of config wizards changed.
        self.company_id.limit_days = self.limit_days

    @api.model
    def get_default_alert_user(self, fields):
        # don't forward-port in v11.0, the API of config wizards changed.
        # digits = self.env.ref('product.decimal_stock_weight').digits
        user_ids = [(4, user.id) for user in self.env.user.company_id.alert_user]
        return {'alert_user': user_ids}

    @api.multi
    def set_alert_user(self):
        # don't forward-port in v11.0, the API of config wizards changed.
        self.company_id.alert_user = self.alert_user

    sent_alert = fields.Selection([
        ('globally', 'Globally'),
        ('category_wise', 'Category Wise'),
        ('warehouse_wise', 'Warehouse Wise')
    ], string="Sent Alert")

    limit_days = fields.Integer("Limits Days")

    alert_user = fields.Many2many('res.users', string="Select User")

    # display_message_category_wise = fields.Char("Message", placeholder="You Can Set Limit Days And User EMail Alert Directly From Company Setting Configuration")

    # display_message_warehouses_wise = fields.Char("Message", placeholder="You Can Set Limit Days And User EMail Alert Directly From WareHouse Setting Configuration")


class THProductCategory(models.Model):
    _inherit = "product.category"

    sent_alert = fields.Selection([
        ('globally', 'Globally'),
        ('category_wise', 'Category Wise'),
        ('warehouse_wise', 'Warehouse Wise')
    ], string="Sent Alert", compute="get_sent_alert")
    limit_days = fields.Integer("Limits Days")
    alert_user = fields.Many2many('res.users', string="Select User")

    @api.one
    def get_sent_alert(self):
        self.sent_alert = self.env.user.company_id.sent_alert


class THStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sent_alert = fields.Selection([
        ('globally', 'Globally'),
        ('category_wise', 'Category Wise'),
        ('warehouse_wise', 'Warehouse Wise')
    ], string="Sent Alert", compute="get_sent_alert")
    limit_days = fields.Integer("Limits Days")
    alert_user = fields.Many2many('res.users', string="Select User")

    @api.one
    def get_sent_alert(self):
        self.sent_alert = self.env.user.company_id.sent_alert


class THProduct(models.Model):

    _inherit = "product.product"

    stock_move_ids = fields.One2many('stock.move', 'product_id', help='Technical: used to compute quantities.')
    move_days = fields.Integer('Days', help="Slow Moving Days")

    # TODO : Make a field here for storing number of days from last_move_date.
    # It will be integer field                                                          ==== Done
    # It will be calculated in the same function.                                       ==== Done
    # It should be done in the both product.product and product.template.               ==== Done(P.T.Remaining)

    @api.model
    def days_cron(self):
        cur_recs = self.search([('last_move_date', '!=', False)])
        cur_recs.compute_days()

    @api.model
    def limit_days(self):
        limit_recs = self.search([('move_days', "!=", False)])
        limit_recs.limit_days_cal()

    @api.multi
    def limit_days_cal(self):
        for product in self:
            if product.move_days > product.categ_id.limit_days:
                print("%s product is gone beyond  the limit" % product.name)

    @api.multi
    @api.depends(
        "stock_move_ids.product_id",
        "stock_move_ids.state")
    def get_last_movement_datetime(self):
        if self.type != 'product':
            return
        for product in self:
            qry = """
            select sm.date 
            from stock_move as sm, stock_picking_type as spt 
            where sm.product_id=%s and sm.state='done' and sm.picking_type_id=spt.id and spt.code='outgoing' 
            order by sm.date desc limit 1;""" % product.id
            self.env.cr.execute(qry)
            result = self.env.cr.fetchall()
            print(result)
            if result:
                product.last_move_date = result[0][0]

    # Compute field will works when it is read from somewhere else.....
    last_move_date = fields.Date("Last Movement", compute="get_last_movement_datetime", store=True)

    # method for send_email_alert
    @api.model
    def send_email_alert(self):
        if self.env.user.company_id.sent_alert == 'globally':
            product_recs = self.env["product.product.report"].create({'sent_alert': self.env.user.company_id.sent_alert})
            print("product_res", product_recs)
            template = self.env.ref('stock_movement.email_alert_template')
            print("template", template)

            template.send_mail(product_recs.id)
        if self.env.user.company_id.sent_alert == 'category_wise':
            category_recs = self.env['product.category'].search([('limit_days', '>', 0), ('alert_user', '!=', False)])
            for category_rec in category_recs:
                product_recs = self.env["product.product.report"].create({
                    'sent_alert': self.env.user.company_id.sent_alert,
                    'current_category_id': category_rec.id})
                print("product_res", product_recs)
                template = self.env.ref('stock_movement.email_alert_template')
                print("template", template)

                template.send_mail(product_recs.id)
        if self.env.user.company_id.sent_alert == 'warehouse_wise':
            warehouse_recs = self.env['stock.warehouse'].search([('limit_days', '>', 0), ('alert_user', '!=', False)])
            for warehouse_rec in warehouse_recs:
                product_recs = self.env["product.product.report"].create({
                    'sent_alert': self.env.user.company_id.sent_alert,
                    'current_warehouse_id': warehouse_rec.id})
                print("product_res", product_recs)
                template = self.env.ref('stock_movement.email_alert_template')
                print("template", template)

                template.send_mail(product_recs.id)


    # method for select multiple email address


    @api.multi
    def compute_days(self):
        print("called")
        for rec in self:
            print("rec called")
            if rec.last_move_date:
                current_date = datetime.today()
                print("Current Date id", current_date)
                days_object = datetime.strptime(rec.last_move_date, df)
                print("Date", days_object)
                days = (current_date - days_object).days
                print(days)
                rec.move_days = days
                print("Days--->>>>", (current_date - days_object).days)

            if rec.move_days >= 30:
                print("%s product is beyond the time limit" % rec.name)


class THProductTemplate(models.Model):

    _inherit = "product.template"

    @api.multi
    @api.depends(
        "product_variant_ids",
        "product_variant_ids.stock_move_ids",
        "product_variant_ids.stock_move_ids.state",
        "product_variant_ids.stock_move_ids.product_id")
    def get_last_movement_datetime(self):
        for product_temps in self:
            last_dates = [
                datetime.strptime(
                    product.last_move_date, df
                ) for product in product_temps.product_variant_ids if product.last_move_date]
            if last_dates:
                product_temps.last_move_date = max(last_dates).strftime(df)

    # Compute field will works when it is read from somewhere else.....
    last_move_date = fields.Datetime("Last Movement", compute="get_last_movement_datetime", store=True)
#
#     @api.one
#     @api.depends('move_days')
#     def compute_days(self):
#         if self.last_move_date:
#             max_date_template = max(last_dates).strftime(df)
#             print("Current Date id", max_date_template)
#             days_object = datetime.strptime(self.last_move_date, df)
#             # print("Date", days_object)
#             days = (max_date_template - days_object).days
#             print(days)
#             self.move_days = days
#             # print("Days--->>>>", (current_date - days_object).days)


"""
40
76
88
96
54

69.4


Jema field upar thi aapde several reports generate karvasna hoy store true


1 j vaar store karvani ???

jana par this reports generate karvanan na lhoy ene store nai karvani








Fields 2 Type
1-> User pase thi input lavanu field.....

2-> computational field jema user na input ni jarur nathi ...... aena previous input par this kai value calculate karvani 6e.......
------> value ne database ma store karvi 6e ke nathi karvi ?

------------>> karvi database ma store karvi 6e......
---------------------->

"""

# class StockMovement(models.Model):
#
#     _name = "stock.movement"
#
#     from_date = fields.Datetime(string="From  Date", required="True")
#     to_date = fields.Datetime(string="To  Date", required="True")
#     demo = fields.Char(string="demo")
#
#     @api.multi
#     def generate(self):
#         product_list = []
#         picking_type_obj = self.env["stock.picking.type"]  # this is  how we can have an odoo object
#
#         picking_type_recs = picking_type_obj.search([('code', '=', 'outgoing')])
#         for rec_id in picking_type_recs:
#
#             generate_obj_rec = self.env["stock.picking"].search([('state', '=', 'done'),
#                                                                  ('picking_type_id', '=', rec_id.id)])
#
#             for rec_id_s in generate_obj_rec:
#
#
#                 for move in rec_id_s.move_lines:
#                     product_list.append(move.product_id.id)
#
#
#         non_moves_product_ids = []
#
#         non_move_product_id = self.env["product.template"].search([('id', 'not in', product_list)])
#         print ("ids", non_move_product_id)
#
#         # for name in non_move_product_id:
#         #     print ("name", name.name)
#         # non_moves_product_ids.append(list_ids.id)
#         # print ("fdfdf", list_ids)
#
#         for list_ids in non_move_product_id:
#             non_moves_product_ids.append(list_ids.id)
#             #
#             # for name in list_ids:
#             #     print('dddfgsfgd', name)
#
#         # print('DDDDD', non_moves_product_ids)
#         view = self.env.ref('stock_movement.product_template_tree_stock_view')
#
#         return {
#             'name': 'Unmoved Products',
#             'view_type': 'form',
#             'view_mode': 'tree',
#             'res_model': 'product.template',
#             'view_id': [view.id],
#             'domain': [('id', 'in', non_moves_product_ids)],
#             'type': 'ir.actions.act_window',
#         }


