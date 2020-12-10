import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


class ProductTask(models.Model):
    _name = 'product.task'
    _description = 'Product Task'

    outplacement_id = fields.Many2one('outplacement', 'Outplacement')
    activity_id = fields.Many2one('res.joint_planning', 'Activity')
    joint_planing_type = fields.Selection([
        ('kvl', 'KVL'),
        ('preplaning', 'Preplaning'),
        ('endraport', 'Endraport'),
    ], 'JP_Type')
