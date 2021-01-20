# coding: utf-8

from odoo import api, fields, models
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def partnersyncCrm2DafaSSN(self,ssn):
        partner = self.sudo().search([('social_sec_nr','=',ssn)],limit=1)
        return {
            'partner': self.sudo().search_read([('social_sec_nr','=',ssn)],limit=1)[0],
            'education_ids': [(e.sun_id.code,e.education_level_id.name, e.foreign_education,e.foreign_education_approved) for e in partner.education_ids],
            # ~ 'education_level': partner.education_level.mapped('name'),
            'drivers_license_ids': partner.drivers_license_ids.mapped('name'),
            'job_ids': [(job.ssyk_code,job.education_level.name,job.experience_length,job.education,job.experience) for job in partner.job_ids],
        }
    @api.model
    def management_teamsyncCrm2Dafa(self,email):
        return self.sudo().search_read([('email','=',email)],limit=1)