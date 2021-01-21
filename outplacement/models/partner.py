from odoo import api, fields, models, tools, _


class Partner(models.Model):
    _inherit = 'res.partner'

    jobseeker_operation_id = fields.Many2one(
        comodel_name='performing.operation', string='Perf. Op. Jobseeker')
    performing_operation_id = fields.Many2one(
        comodel_name='performing.operation', string='Performing Operation',
        help="This is an address for the given Performing Operation")


class Users(models.Model):
    _inherit = 'res.users'

    performing_operation_ids = fields.Many2many(
        comodel_name='performing.operation',
        string='Performing Operations',
        relation='performing_operation_user_rel',
        column1='user_id',
        column2='operation_id')
