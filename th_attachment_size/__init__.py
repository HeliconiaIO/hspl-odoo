# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['ir.model.data'].search(
        [('model', '=', 'ir.attachment')])