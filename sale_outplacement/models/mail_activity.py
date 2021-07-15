# -*- coding: utf-8 -*-

from odoo import models, fields


class MailActivityTemplate(models.Model):
    _name = "mail.activity.template"
    _description = "Mail Activity Template"

    # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate
    product_id = fields.Many2one(comodel_name='product.product')
    due_days = fields.Integer()
    activity_type_id = fields.Many2one(comodel_name='mail.activity.type',
                                       string='Activity')
    summary = fields.Char('Summary')
