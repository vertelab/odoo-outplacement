from odoo import models, fields

class Outplacement(models.Model):
    _inherit = "outplacement"

    social_sec_nr = fields.Char(string="Social security number", related="partner_id.social_sec_nr")