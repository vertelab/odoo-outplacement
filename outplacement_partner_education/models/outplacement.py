from odoo import models, fields

class Outplacement(models.Model):
    _inherit = "outplacement"

    education_ids = fields.One2many(string="Educations", comodel_name="res.partner.education", inverse_name="partner_id", related="partner_id.education_ids", readonly=False)    
    cv = fields.Binary('CV', related="partner_id.cv", readonly=False)
    cv_file_name = fields.Char(related="partner_id.cv_file_name", readonly=False)
    references = fields.Binary(related="partner_id.references", readonly=False)
    references_file_name = fields.Char(related="partner_id.references_file_name", readonly=False)
    has_drivers_license = fields.Boolean(string="Has drivers license",
                                         compute='_compute_has_drivers_license', related="partner_id.has_drivers_license", readonly=False)
    drivers_license_ids = fields.One2many(comodel_name='res.drivers_license',
                                          inverse_name='partner_id',
                                          string='Drivers license class', related="partner_id.drivers_license_ids", readonly=False)
    has_car = fields.Boolean(string="Has access to car", related="partner_id.has_car", readonly=False)