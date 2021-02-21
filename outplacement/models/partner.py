from odoo import api, fields, models, tools, _  # noqa:F401


class Partner(models.Model):
    _inherit = 'res.partner'

    performing_operation_ids = fields.One2many(
        comodel_name="performing.operation",
        inverse_name="company_id",
        string="Performing operations",
        related="company_id.performing_operation_ids",
        )
    jobseeker_operation_id = fields.Many2one(
        comodel_name='performing.operation', string='Perf. Op. Jobseeker')
    performing_operation_id = fields.Many2one(
        comodel_name='performing.operation', string='Performing Operation',
        help="This is an address for the given Performing Operation")
    # Logically this should be a one2one, but this makes it update
    # correctly if outplacement changes.
    outplacement_ids = fields.One2many(
        comodel_name="outplacement",
        inverse_name="partner_id",
        string="Outplacement"
        )

class Users(models.Model):
    _inherit = 'res.users'

    performing_operation_ids = fields.Many2many(
        comodel_name='performing.operation',
        string='Performing Operations',
        relation='performing_operation_user_rel',
        column1='user_id',
        column2='operation_id')


class ResCompany(models.Model):
    _inherit = "res.company"

    performing_operation_ids = fields.One2many(
        comodel_name="performing.operation",
        inverse_name="company_id",
        string="Performing operations"
        )
