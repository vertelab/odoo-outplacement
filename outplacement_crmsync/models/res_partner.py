# coding: utf-8

from xmlrpc.client import ServerProxy
from odoo import api, fields, models
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class crm_server(object):

    def __init__(self,env):
        
        self.server_url =  env['ir.config_parameter'].sudo().get_param('outplacement_crmsync.server_url','http[s]://<domainn>')
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

class Outplacement(models.Model):
    _inherit = 'outplacement'

    @api.one
    def get_jobseeker_fields(self):
        return ['name', 'street', 'comment']

    @api.one
    def get_jobseeker_data(self):
        
        xmlrpc = crm_server(self.env)        
        partner_rec = xmlrpc.execute(
            'res.partner', 'search_read',
                [
                    # ~ [['social_sec_nr', '=', self.social_sec_nr]],
                    [[]],
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

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def get_jobseeker_data(self):
        
        xmlrpc = crm_server(self.env)
