import datetime
import logging  # noqa:F401

from odoo import models, fields, api, _  # noqa:F401
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

    def deliver_interpreter(self):
        if not self.mail_activity_id.interpreter_company:
            raise UserError(_('Could not find an assigned interpreter'))
        if self.mail_activity_id.time_end > datetime.datetime.now():
            raise UserError(_('The occation still lies in the future'))
        client = self.env['ipf.interpreter.client']
        payload = {}
        try:
            response = client.put_tolkbokningar_id_inleverera(self.booking_ref,
                                                              payload)
        except Exception as e:
            _logger.exception(e)
        else:
            if response.status_code in ('200', ):
                self.log_to_accounting()
            else:
                raise UserError('Failed to deliver interpreter with:\n'
                                f'{response.status_code}\n'
                                f'{response.text}')

    def log_to_accounting(self):
        analytic_id = self.mail_activity_id.get_outplacement_value(
            'analytic_account_id')
        start = self.mail_activity_id.time_start
        end = self.mail_activity_id.time_end
        td = end - start + datetime.timedelta(minutes=self.additional_time)
        hours = td.total_seconds() // 3600

        self.env['account.analytic.line'].create({
            'amount': 0.0,
            'unit_amount': hours,
            'name': f'Tolk: {self.mail_activity_id.interpreter_name}',
            'date': datetime.datetime.now(),
            'account_id': analytic_id.id})
