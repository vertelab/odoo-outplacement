from odoo import models, fields, api, _

class Outplacement(models.Model):
    _inherit = "outplacement"

    social_sec_nr = fields.Char(string="Social security number")

    @api.onchange('social_sec_nr')
    def set_partner_ssn(self):
        if self.partner_id:
            self.partner_id.write({'social_sec_nr': self.social_sec_nr})
        else:
            self.social_sec_nr = False
    
    @api.onchange('partner_id')
    def load_partner_values(self):
        super(Outplacement, self).load_partner_values()
        self.social_sec_nr = self.partner_id.social_sec_nr
        