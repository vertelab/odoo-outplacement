from odoo import models, fields, api, _

class Outplacement(models.Model):
    _inherit = "outplacement"

    job_ids = fields.One2many(comodel_name="res.partner.jobs", inverse_name="outplacement_id")

    @api.onchange('job_ids')
    def set_partner_jobs(self):
        if self.partner_id:
            self.partner_id.write({'job_ids': [(6,0,self.job_ids._ids)]})
        else:
            self.job_ids = False

    @api.onchange('partner_id')
    def load_partner_values(self):
        super(Outplacement, self).load_partner_values()
        self.job_ids = [(6,0,self.partner_id.jobs_ids._ids)]

class Jobs(models.Model):
    _inherit = 'res.partner.jobs'

    outplacement_id = fields.Many2one(comodel_name='outplacement')