from odoo import models, fields


class Outplacement(models.Model):
    _inherit = "outplacement"

    interpreter_language = fields.Many2one(
        related="partner_id.interpreter_language",
        readonly=False)
    interpreter_gender_preference = fields.Many2one(
        related="partner_id.interpreter_gender_preference",
        readonly=False)
    # interpreter_type = fields.Many2one()
    # interpreter_remote_type = fields.Many2one()
