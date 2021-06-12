import logging

from odoo import api, fields, models, tools, _  # noqa:F401

_logger = logging.getLogger(__name__)


class PerformingOperation(models.Model):
    _name = 'performing.operation'
    _description = 'Performing Operation'

    name = fields.Char()
    ka_nr = fields.Integer(string='KA Number',
                           help="Utförande verksamhets-nummer")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    partner_ids = fields.One2many(comodel_name='res.partner',
                                  string='Addresses',
                                  inverse_name='performing_operation_id')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users',
        relation='performing_operation_user_rel',
        column1='operation_id',
        column2='user_id')
