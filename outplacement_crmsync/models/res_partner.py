# coding: utf-8

from xmlrpc.client import ServerProxy
from odoo import api, fields, models
from odoo.exceptions import Warning
import odoorpc

import logging
_logger = logging.getLogger(__name__)

class crm_server(object):

    def __init__(self,env):
        
        self.server_url =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_url','http[s]://<domain>')
        self.server_port = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_port','8069')
        self.server_db =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_db','database')
        self.server_login = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_login','userid')
        self.server_pw =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_pw','password')

        self.url_common = f'{self.server_url}:{self.server_port}/xmlrpc/2/common'
        
        try:
            self.common = ServerProxy(self.url_common)
            self.uid = self.common.authenticate(self.server_db, self.server_login,self.server_pw, {})
        except Exception as e:
            raise Warning('Login %s' % e)
        
        self.url_model = f'{self.server_url}:{self.server_port}/xmlrpc/2/object'
        try:
            self.model = ServerProxy(self.url_model)
        except Exception as e:
            raise Warning('Model %s ' % e)
        
    def execute(self,model,command,param):
        return self.model.execute_kw(self.server_db, self.uid, self.server_pw,
                                    model,command,param)
class crm_serverII(object):

    def __init__(self,env):
        
        self.server_url =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_url','http[s]://%s')
        self.server_host =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_host','<domain>')
        self.server_port = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_port','8069')
        self.server_db =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_db','database')
        self.server_login = env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_login','userid')
        self.server_pw =   env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_pw','password')

        
        try:
            self.common = odoorpc.ODOO(host=self.server_host,port=self.server_port)
            self.common.login(db=self.server_db,login=self.server_login,password=self.server_pw)
        except Exception as e:
            raise Warning('Login %s' % e)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    @api.multi
    def get_jobseeker_fields(self):
        return ['name', 'street', 'comment']

    @api.one
    def get_jobseeker_data(self):
        
        xmlrpc = crm_server(self.env)        
        partner_rec = xmlrpc.execute(
            'res.partner', 'search_read',
                [
                    # ~ [['social_sec_nr', '=', self.social_sec_nr]],
                    [['id','=',26]],
                    {'fields': ['name', 'street','street2','zip','city','phone','email',], 'limit': 1}
                ]
            )
        
        # ~ self.write({'partner_name': partner_rec['name'],
                    # ~ 'partner_street': partner_rec['street'],
                    # ~ 'partner_street2': partner_rec['street2'],
                    # ~ 'partner_zip': partner_rec['zip'],
                    # ~ 'partner_city': partner_rec['city'],
                    # ~ 'partner_email': partner_rec['email']})
        self.partner_id.write(partner_rec)
        
    @api.one
    def get_jobseeker_dataII(self):
        
        xmlrpc = crm_serverII(self.env)
        
        

        
        partner = xmlrpc.common.env['res.partner'].browse(
            xmlrpc.common.env['res.partner'].search([('social_sec_nr','=',self.social_sec_nr)],limit=1))
            # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
            
        self.write({
            'name': partner.name,
            'street': partner.street,
            'street2': partner.street2,
            'zip': partner.zip,
            'city': partner.city,
            'phone': partner.phone,
            'email': partner.email,
            #
            # outplacement_education
            #
            'sun_ids': [(6,0,[c.id for c in self.env['res.sun'].search([('code','in',partner.sun_ids.mapped('code'))])])],
            'education_level': [(6,0,[e.id for e in self.env['res.partner.education_level'].search([('name','in',partner.education_level.mapped('name'))])])],
            'foreign_education': partner.foreign_education,
            'foreign_education_approved': partner.foreign_education_approved,
            'cv': partner.cv,
            'cv_file_name': partner.cv_file_name,
            'references': partner.references,
            'references_file_name': partner.references_file_name,
            'has_drivers_license': partner.has_drivers_license,
            'drivers_license_ids': [(6,0,[e.id for e in self.env['res.drivers_license'].search([('name','in',partner.drivers_license_ids.mapped('name'))])])],
            'has_car': partner.has_car,
            # ~ # jobs
            'job_ids': [(6,0,[e.id for e in self.env['res.jobs'].search([('name','in',partner.job_ids.mapped('name'))])])],
            # skills
                # ~ skills = fields.Many2many('hr.skill', string="Skill")
    # ~ skill_id = fields.Char(string="Skill", related="skills.complete_name")

    # ~ other_experiences = fields.Many2many(comodel_name='outplacement.other_experiences', string="Other Experience")
    # ~ strengths = fields.Many2many(comodel_name='outplacement.strengths', string="Strengths")
    # ~ interests = fields.Many2many(comodel_name='outplacement.interests', string="Interests")
    # ~ partner_skill_ids = fields.One2many(
        # ~ string='Skills',
        # ~ comodel_name='hr.employee.skill',
        # ~ inverse_name='partner_id',
    # ~ )
            
        }) 
        
    @api.one
    def get_jobseeker_dataIII(self):
        """
        Test utan komplexa data
        """
        
        xmlrpc = crm_serverII(self.env)
        
        

        
        partner = xmlrpc.common.env['res.partner'].browse(
            xmlrpc.common.env['res.partner'].search([('social_sec_nr','=',self.social_sec_nr)],limit=1))
            # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
            
        self.write({
            'name': partner.name,
            'street': partner.street,
            'street2': partner.street2,
            'zip': partner.zip,
            'city': partner.city,
            'phone': partner.phone,
            'email': partner.email,
            
        }) 
        
    @api.one
    def get_jobseeker_dataIV(self):
        """
        Test mot demo-data / utan partner_ssn
        """
        
        xmlrpc = crm_serverII(self.env)
        
        

        
        partner = xmlrpc.common.env['res.partner'].browse(
            xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
            # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
            
        self.write({
            'name': partner.name,
            'street': partner.street,
            'street2': partner.street2,
            'zip': partner.zip,
            'city': partner.city,
            'phone': partner.phone,
            'email': partner.email,
        }) 

    @api.one
    def get_af_management_team(self):
        """
        Test update management team
        """
        
        xmlrpc = crm_serverII(self.env)
        
        partner = xmlrpc.common.env['res.partner'].browse(
            xmlrpc.common.env['res.partner'].search([('email','=',self.management_team_id.email)],limit=1))
            # ~ xmlrpc.common.env['res.partner'].search([('id','=',26)],limit=1))
        if self.management_team_id._name == 'hr.employee':
            self.management_team_id.write({
                    'first_name': partner.first_name,
                    'last_name': partner.last_name,
                    'work_phone': partner.phone,
                    'work_email': partner.email,
                })
        else:
            self.management_team_id.write({
                    'first_name': partner.first_name,
                    'last_name': partner.last_name,
                    'street': partner.street,
                    'street2': partner.street2,
                    'zip': partner.zip,
                    'city': partner.city,
                    'phone': partner.phone,
                    'email': partner.email,
                })


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def get_jobseeker_data(self):
        
        xmlrpc = crm_server(self.env)
