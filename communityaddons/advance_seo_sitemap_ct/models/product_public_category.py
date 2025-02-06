# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools

class product_public_category(models.Model):
    _inherit = 'product.public.category'

    frequency = fields.Selection([('daily', 'Daily'),('monthly','Monthly'),('never','Never')], string='Frequency')
    priority = fields.Selection([('0.0', '0.0'),('0.1', '0.1'),('0.2', '0.2'),('0.3', '0.3'),('0.4', '0.4'),('0.5', '0.5'),('0.6', '0.6'),('0.7', '0.7'),('0.8', '0.8'),('0.9', '0.9'),('1.0', '1.0')], string='Priority')