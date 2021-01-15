from odoo import models, fields

class Outplacement(models.Model):
    _inherit = "outplacement"

    interpreter_language = fields.Selection(related="partner_id.interpreter_language", readonly=False)
    interpreter_gender_preference = fields.Selection(related="partner_id.interpreter_gender_preference", readonly=False)