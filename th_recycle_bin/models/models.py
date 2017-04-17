# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class RecycleBin(models.Model):
    
    _name = 'th.recycle.bin'
    
    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Document Model', required=True, domain=[('transient', '=', False)])
    model = fields.Char(related='model_id.model', readonly=True)
    active = fields.Boolean(default=True, help="When unchecked, the rule is hidden and will not be executed.")
    auto_delete = fields.Boolean('Auto Flush?', help="If checked, Scheduler will delete the record after a week")
    
    @api.model_cr
    def _register_hook(self):
        def make_unlink():
            @api.multi
            def unlink(self, **kwargs): 
                return unlink.origin(self, **kwargs)
            return unlink
        
        patched_models = defaultdict(set)
        def patch(model, name, method):
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)
                
        for bin in self.with_context({}).search([]):
            Model = self.env[bin.model]
            patch(Model, 'unlink', make_unlink())
    
    
    @api.model
    def create(self, vals):
        
        return super(RecycleBin, self).create(vals)