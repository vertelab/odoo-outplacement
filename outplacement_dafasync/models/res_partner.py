# coding: utf-8

from odoo import api, fields, models
from odoo.exceptions import Warning

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def partnersyncCrm2DafaSSN(self,ssn):
        partner = self.sudo().search([('social_sec_nr','=',ssn)],limit=1)
        if not partner:
            return False
        values = {
            "partner": self.sudo().search_read([("social_sec_nr", "=", ssn)], limit=1)[
                0
            ],
            "education_ids": [
                (
                    e.sun_id.code,
                    e.education_level_id.name,
                    e.foreign_education,
                    e.foreign_education_approved,
                )
                for e in partner.education_ids
            ],
            "drivers_license_ids": partner.drivers_license_ids.mapped("name"),
        }
        job_ids = []
        for job in partner.job_ids:
            job_tuple = (
                job.ssyk_code,
                job.experience_length,
                job.experience,
                job.education,
            )

            if job.education_id:
                job_tuple = job_tuple + (
                    job.education_id.sun_id.code,
                    job.education_id.education_level_id.name,
                    job.education_id.foreign_education,
                    job.education_id.foreign_education_approved,
                )

            job_tuple = job_tuple + ()
            job_ids.append(job_tuple)
        values["job_ids"] = job_ids
        if partner.jobseeker_category_id:
            values["jobseeker_category_code"] = partner.jobseeker_category_id.code
        return values

    @api.model
    def management_teamsyncCrm2Dafa(self, email):
        return self.sudo().search_read([("email", "=", email)], limit=1)
