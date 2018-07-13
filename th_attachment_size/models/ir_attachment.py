# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.depends('file_size')
    def convert_size(self):
        for rec in self:
            if rec.file_size == 0:
                return "0B"
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(rec.file_size, 1024)))
            p = math.pow(1024, i)
            s = round(rec.file_size / p, 2)
            rec.size = "%s %s" % (s, size_name[i])

    size = fields.Char('File Size',compute='convert_size', store=True)