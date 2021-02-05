# coding: utf-8

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed().append(('en_US',
                                                            'American'))
    interpreter_language = fields.Many2one(
        comodel_name='res.interpreter.language',
        string='Interpreter Language')
    interpreter_gender_preference = fields.Many2one(
        comodel_name='res.interpreter.gender_preference',
        string='Gender Preference')
