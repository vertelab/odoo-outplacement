from odoo import models, fields

class Outplacement(models.Model):
    _inherit = "outplacement"

    job_ids = fields.One2many(comodel_name="res.partner.jobs", inverse_name="partner_id", related="partner_id.job_ids", readonly=False)