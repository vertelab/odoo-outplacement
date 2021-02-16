import logging  # noqa:F401

from odoo import models, fields, api, __  # noqa:F401
from odoo.exceptions import UserError, Warning  # noqa:F401

_logger = logging.getLogger(__name__)


class InterpreterDeliveryWizard(models.TransientModel):
    _name = 'outplacement.interpreter_delivery.wizard'
    mail_activity_id = fields.Many2one(
        comodel_name='mail.activity', string='Mail Activity',
        default=lambda self: self.env['mail.activity'].browse(
            self.env.context.get('active_id')))
    booking_ref = fields.Char(
        string='Interpreter Booking Reference',
        related='mail_activity_id.interpreter_booking_ref',
        readonly=True)
    kanr = fields.Char(string='KA-Number',
                       default=lambda self: self.get_ka_nr(),
                       readonly=True)
    absent_interpreter = fields.Boolean(string='Absent interpreter',
                                        default=False)
    additional_time = fields.Integer(string='Additional time (minutes)',
                                     default=0)

    # Followup code and office code are not currently used by
    # tolkportalen.
    follow_up_code = fields.Integer(string='Follow up code')
    office_code = fields.Integer(string='Office code')
    project_code = fields.Integer(string='Project code')

    def get_ka_nr(self):
        # Cannot use self.mail_activity_id here as it has not been set
        # when initiating the class.
        mail_activity_id = self.env['mail.activity'].browse(
            self.env.context.get('active_id'))
        perf_op = mail_activity_id.get_outplacement_value(
             'performing_operation_id')
        return perf_op.ka_nr
