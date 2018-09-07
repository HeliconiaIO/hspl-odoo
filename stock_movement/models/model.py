
from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class THProduct(models.Model):

    _inherit = "product.product"

    stock_move_ids = fields.One2many('stock.move', 'product_id', help='Technical: used to compute quantities.')

    @api.multi
    @api.depends("stock_move_ids.product_id")
    def get_last_movement_datetime(self):
        for product in self:
            qry = "select date from stock_move where product_id=%s and state='done' order by date limit 1;" % product.id
            self.env.cr.execute(qry)
            result = self.env.cr.fetchall()
            if result:
                product.last_move_date = result[0][0]

    # Compute field will works when it is read from somewhere else.....
    last_move_date = fields.Datetime("Last Movement", compute="get_last_movement_datetime", store=True)


class THProductTemplate(models.Model):

    _inherit = "product.template"

    @api.multi
    @api.depends(
        "product_variant_ids",
        "product_variant_ids.stock_move_ids",
        "product_variant_ids.stock_move_ids.product_id")
    def get_last_movement_datetime(self):
        print("Method has been calleddddd \n\n\n\n")
        for product_temps in self:
            last_dates = [
                datetime.strptime(
                    product.last_move_date, DEFAULT_SERVER_DATETIME_FORMAT
                ) for product in product_temps.product_variant_ids if product.last_move_date]
            if last_dates:
                product_temps.last_move_date = max(last_dates).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    # Compute field will works when it is read from somewhere else.....
    last_move_date = fields.Datetime("Last Movement", compute="get_last_movement_datetime", store=True)


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

class StockMovement(models.Model):

    _name = "stock.movement"

    from_date = fields.Datetime(string="From  Date", required="True")
    to_date = fields.Datetime(string="To  Date", required="True")
    demo = fields.Char(string="demo")

    @api.multi
    def generate(self):
        product_list = []
        picking_type_obj = self.env["stock.picking.type"]  # this is  how we can have an odoo object

        picking_type_recs = picking_type_obj.search([('code', '=', 'outgoing')])
        for rec_id in picking_type_recs:

            generate_obj_rec = self.env["stock.picking"].search([('state', '=', 'done'),
                                                                 ('picking_type_id', '=', rec_id.id)])

            for rec_id_s in generate_obj_rec:


                for move in rec_id_s.move_lines:
                    product_list.append(move.product_id.id)


        non_moves_product_ids = []

        non_move_product_id = self.env["product.template"].search([('id', 'not in', product_list)])
        print ("ids", non_move_product_id)

        # for name in non_move_product_id:
        #     print ("name", name.name)
        # non_moves_product_ids.append(list_ids.id)
        # print ("fdfdf", list_ids)

        for list_ids in non_move_product_id:
            non_moves_product_ids.append(list_ids.id)
            #
            # for name in list_ids:
            #     print('dddfgsfgd', name)

        # print('DDDDD', non_moves_product_ids)
        view = self.env.ref('stock_movement.product_template_tree_stock_view')

        return {
            'name': 'Unmoved Products',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.template',
            'view_id': [view.id],
            'domain': [('id', 'in', non_moves_product_ids)],
            'type': 'ir.actions.act_window',
        }


