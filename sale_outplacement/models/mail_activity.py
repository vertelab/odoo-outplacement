# -*- coding: utf-8 -*-

from odoo import models, fields


class MailActivity(models.Model):
    _inherit = "mail.activity"

    due_days = fields.Integer()
