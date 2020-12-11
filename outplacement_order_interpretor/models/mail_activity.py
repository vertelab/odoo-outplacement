# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    interpreter_language = fields.Selection(
        _lang_get, default=lambda self: self.env.lang)
    interpreter_gender_preference = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('no_preference', 'no preference'),
    ])
    location_type = fields.Selection([
        ('on_premise', 'On premise'),
        ('telephone', 'Telephone'),
    ], 'Location')
    time_start = fields.Datetime('Start Time')
    time_end = fields.Datetime('End Time')
    phone = fields.Char()
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')

    @api.multi
    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary or self.res_name,
            'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
            'initial_date': self.date_deadline,
        }
        return action
