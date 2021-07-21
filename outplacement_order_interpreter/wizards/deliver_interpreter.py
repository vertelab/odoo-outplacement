import datetime
import json
import logging
from odoo.exceptions import UserError

from odoo import models, fields, api, _  # noqa:F401

_logger = logging.getLogger(__name__)


class InterpreterDeliveryWizard(models.TransientModel):
    """Wizard for delivery of an interpreter booking."""
    _name = 'outplacement.interpreter_delivery.wizard'
    _description = "Outplacement Intepreter Delivery Wizard"

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
    follow_up_code = fields.Char(string='Follow up code')
    office_code = fields.Char(string='Office code')
    project_code = fields.Char(string='Project code')

    def get_ka_nr(self):
        """Gets KA number from parents parent (Outplacement)."""
        # Cannot use self.mail_activity_id here as it has not been set
        # when initiating the class.
        mail_activity_id = self.env['mail.activity'].browse(self.env.context.get('active_id'))
        perf_op = mail_activity_id.get_outplacement_value('performing_operation_id')
        if perf_op:
            return perf_op.ka_nr
        else:
            return ''

    def deliver_interpreter(self):
        """Deliver interpreter booking to Tolkportalen."""
        self.validate_data()
        client = self.env['ipf.interpreter.client'].search([], limit=1)
        payload = {'extraMinuter': self.additional_time,
                   'kanr': self.kanr,
                   'uteblivenTolk': self.absent_interpreter,
                   'projektkod': self.project_code or '',
                   'uppfoljningskategorikod': self.follow_up_code or '',
                   'kontorskod': self.office_code or ''}
        _logger.debug(payload)
        try:
            response = client.put_tolkbokningar_id_inleverera(self.booking_ref,
                                                              payload)
        except Exception as e:
            _logger.exception(e)
            _logger.error(payload)
        else:
            self.check_response(response)
            self.log_to_accounting()
            self.log_to_activity_stream()
            self.mail_activity_id.action_done()

    def validate_data(self):
        if self.additional_time % 15:
            raise UserError(_('Additional time has to be in 15 min '
                              'increments'))
        if not self.mail_activity_id.interpreter_company:
            raise UserError(_('Could not find an assigned interpreter'))
        if self.mail_activity_id.time_start > datetime.datetime.now():
            raise UserError(_('The occation still lies in the future'))

    def check_response(self, response):
        """Verify that response is 200 else raise UserError."""
        try:
            status_code = response.status_code
        except AttributeError:
            _logger.exception(_('Could not access status code in response'))
            raise UserError(_('Could not access status code in response'))
        error_codes = {400: 'Faulty params\n{msg}',
                       403: 'Faulty credentials\n{msg}',
                       404: 'Faulty reference ({ref}),'
                            'could not find booking\n{msg}',
                       500: 'Unknown Error\n{msg}'}
        if status_code in (200,):
            return
        elif status_code in error_codes:
            msg = json.loads(response.text).get('message')
            ref = self.mail_activity_id.interpreter_booking_ref
            _logger.exception(error_codes[status_code].format(
                ref=ref, msg=msg))
            raise UserError(_(error_codes[status_code]).format(
                ref=ref, msg=msg))
        else:
            msg = 'Unkown status_code:\n ' \
                  '{response.status_code}\n{response.text}'
            _logger.error(msg.format(response=response))
            raise UserError(_(msg).format(response=response))

    def log_to_activity_stream(self):
        activity = self.mail_activity_id
        subject = _('Interpreter Booking')
        msg = _('Interpreter booking with reference: {ref} delivered').format(
            ref=activity.interpreter_booking_ref)

        self.env['mail.message'].create({
            'body': f"{subject}<br>{msg}",
            'subject': _("Interpreter Delivery"),
            'author_id': self.env['res.users'].browse(
                self.env.uid).partner_id.id,
            'res_id': activity.res_id,
            'model': activity.res_model,
        })
        activity.additional_time = self.additional_time

    def log_to_accounting(self):
        """Create an accounting row with the amount of hours logged."""
        activity = self.mail_activity_id
        analytic_id = activity.get_outplacement_value('analytic_account_id')
        extra = datetime.timedelta(minutes=self.additional_time)
        timedelta = activity.time_end - activity.time_start + extra

        self.env['account.analytic.line'].create({
            'amount': 0.0,
            'unit_amount': timedelta.total_seconds() / 3600,
            'name': f'Tolk: {activity.interpreter_name} '
                    f'Ref:{activity.interpreter_booking_ref}',
            'date': datetime.datetime.now(),
            'account_id': analytic_id.id})
