import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    ka_ref = fields.Char('KA-Number')
