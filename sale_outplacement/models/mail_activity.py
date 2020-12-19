# -*- coding: utf-8 -*-

from odoo import models, fields

class MailActivityTemplate(models.Model):
    _name = "mail.activity.template"

    due_days = fields.Integer()
    activity_type_id = fields.Many2one(comodel_name='mail.activity.type', 
                                       string='Activity')
    summary = fields.Char('Summary')


