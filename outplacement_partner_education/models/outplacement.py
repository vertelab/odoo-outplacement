from odoo import models, fields, api, _

class Outplacement(models.Model):
    _inherit = "outplacement"

    sun_ids = fields.Many2many(comodel_name='res.sun',
                               string='SUN Code')
    education_level = fields.Many2one(
        comodel_name="res.partner.education_level",
        string="Education level")
    foreign_education = fields.Boolean(string="Foreign education")
    foreign_education_approved = fields.Boolean(
        string="Foreign education approved")
    cv = fields.Binary('CV')
    cv_file_name = fields.Char()
    references = fields.Binary()
    references_file_name = fields.Char()
    has_drivers_license = fields.Boolean(string="Has drivers license",
                                         compute='_compute_has_drivers_license') 
    drivers_license_ids = fields.One2many(comodel_name='res.drivers_license', 
                            inverse_name='outplacement_id', string='Drivers license class')
    has_car = fields.Boolean(string="Has access to car")

    @api.onchange('education_level', 'foreign_education', 'foreign_education_approved', 'cv_file_name', 'references_file_name', 'has_car')
    def set_partner_data(self):
        if self.partner_id:
            self.partner_id.write({
                'education_level': self.education_level, 
                'foreign_education': self.foreign_education, 
                'foreign_education_approved': self.foreign_education_approved,
                'cv_file_name': self.cv_file_name,
                'references_file_name': self.references_file_name, 
                'has_car': self.has_car
            })
        else:
            self.education_level = False
            self.foreign_education = False
            self.foreign_education_approved = False
            self.cv_file_name = False
            self.references_file_name = False
            self.has_car = False

    @api.onchange('sun_ids')
    def set_partner_sun_ids(self):
        if self.partner_id:
            self.partner_id.write({
                'sun_ids': [(6,0,self.sun_ids._ids)]
            })
        else:
            self.sun_ids = False

    @api.onchange('drivers_license_ids')
    def set_partner_drivers_license(self):
        if self.partner_id:
            self.partner_id.write({
                'drivers_license_ids': [(6,0,self.drivers_license_ids._ids)]
            })
        else:
            self.drivers_license_ids = False

    @api.onchange('cv')
    def set_partner_cv(self):
        if self.partner_id:
            self.partner_id.write({
                'cv': self.cv
            })
        else:
            self.cv = False

    @api.onchange('references')
    def set_partner_references(self):
        if self.partner_id:
            self.partner_id.write({
                'references': self.references
            })
        else:
            self.references = False

    @api.one
    def _compute_has_drivers_license(self):
        self.har_drivers_license = len(self.drivers_license_ids) > 0

    @api.onchange('partner_id')
    def load_partner_values(self):
        super(Outplacement, self).load_partner_values()
        self.sun_ids = [(6,0,self.partner_id.sun_ids._ids)]
        self.education_level = self.partner_id.education_level
        self.foreign_education = self.partner_id.foreign_education
        self.foreign_education_approved = self.partner_id.foreign_education_approved
        self.cv = self.partner_id.cv
        self.cv_file_name = self.partner_id.cv_file_name
        self.references = self.partner_id.references
        self.has_car = self.partner_id.has_car
        self.drivers_license_ids = [(6,0,self.partner_id.drivers_license_ids._ids)]

class ResDriversLicense(models.Model):
    _inherit = 'res.drivers_license'

    outplacement_id = fields.Many2one(comodel_name='outplacement')