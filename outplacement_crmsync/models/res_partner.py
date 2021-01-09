# coding: utf-8

from xmlrpc.client import ServerProxy
from odoo import api, fields, models
from odoo.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def get_jobseeker_data(self):
        
        server_url =  self.env['ir.config_parameter'].get_param('outplacement_crmsync.server_url')
        server_port = self.env['ir.config_parameter'].get_param('outplacement_crmsync.server_port')
        server_db =   self.env['ir.config_parameter'].get_param('outplacement_crmsync.server_db')
        server_login = self.env['ir.config_parameter'].get_param('outplacement_crmsync.server_login')
        server_pw =   self.env['ir.config_parameter'].get_param('outplacement_crmsync.server_pw')

        local_url = f'{server_url}:{server_port}/xmlrpc/common'
        
        try:
            rpc = ServerProxy(local_url, allow_none=True)
            self.uid = rpc.login(server_db, server_login,server_pw)
        except Exception as e:
            raise Warning(e)
        
        uid = rpc.authenticate(server_db, server_login, server_pw, {})

        partner_rec = rpc.execute_kw(server_db, uid, server_pw,
            'res.partner', 'search_read',
            [[['social_sec_nr', '=', self.social_sec_nr]],
            {'fields': ['name', 'country_id', 'comment'], 'limit': 1}])

        self.write(partner_rec)
