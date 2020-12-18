from odoo import models, fields

class Outplacement(models.Model):
    _inherit = "outplacement"

    sun_ids = fields.Many2many(comodel_name='res.sun',
                               string='SUN Code', related="partner_id.sun_ids")
    education_level = fields.Many2one(
        comodel_name="res.partner.education_level",
        string="Education level", related="partner_id.education_level")
    foreign_education = fields.Boolean(string="Foreign education", related="partner_id.foreign_education")
    foreign_education_approved = fields.Boolean(
        string="Foreign education approved", related="partner_id.foreign_education_approved")
    cv = fields.Binary('CV', related="partner_id.cv")
    cv_file_name = fields.Char(related="partner_id.cv_file_name")
    references = fields.Binary(related="partner_id.references")
    references_file_name = fields.Char(related="partner_id.references_file_name")
    has_drivers_license = fields.Boolean(string="Has drivers license",
                                         compute='_compute_has_drivers_license', related="partner_id.has_drivers_license")
    drivers_license_ids = fields.One2many(comodel_name='res.drivers_license',
                                          inverse_name='partner_id',
                                          string='Drivers license class', related="partner_id.drivers_license_ids")
    has_car = fields.Boolean(string="Has access to car", related="partner_id.has_car")