from odoo import api, fields, models, tools, SUPERUSER_ID

# ~ from odoo.addons.outplacement.outplacement_crmsync.models.res_partner import crm_server

class Outplacement(models.Model):
    _inherit = "outplacement"

    job_ids = fields.One2many(comodel_name="res.partner.jobs", inverse_name="partner_id", related="partner_id.job_ids", readonly=False)
    
    # ~ @api.one
    # ~ def get_jobseeker_fields(self):
        # ~ fields = super(Outplacement,self).get_jobseeker_fields()
        # ~ fields.append([])
        # ~ return fields

    # ~ @api.one
    # ~ def get_jobseeker_data(self):

        # ~ super(Outplacement,self).get_jobseeker_data()
        
        # ~ xmlrpc = crm_server(self.env)
        # ~ # read out job_ids
