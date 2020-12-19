
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_suborder = fields.Boolean('is Suborder Product')
    mail_activity_ids = fields.Many2many('mail.activity.template')
