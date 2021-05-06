# -*- coding: utf-8 -*-

from collections import defaultdict
import datetime
import json
import logging
import pytz

from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    active = fields.Boolean(default=True)
    interpreter_language = fields.Many2one(
        comodel_name='res.interpreter.language',
        string='Interpreter Language',
        default=lambda self: self._get_default_outplacement_value(
            'interpreter_language'))
    interpreter_gender_preference = fields.Many2one(
        comodel_name='res.interpreter.gender_preference',
        string="Gender Preference",
        default=lambda self: self._get_default_outplacement_value(
            'interpreter_gender_preference'))
    interpreter_gender = fields.Many2one(
        comodel_name='res.interpreter.gender_preference',
        string='Interpreter Gender',
        readonly=True)
    interpreter_type = fields.Many2one(
        comodel_name='res.interpreter.type',
        string='Interpreter Type',
        domain=[('code', '!=', '1')])
    interpreter_type_code = fields.Char(related='interpreter_type.code')
    interpreter_remote_type = fields.Many2one(
        comodel_name='res.interpreter.remote_type',
        string='Interpreter Remote Type')
    time_start = fields.Datetime(
        'Start Time',
        default=lambda self: self._get_default_task_value('start_date'))
    time_end = fields.Datetime(string='End Time',
                               default=lambda self: self._get_end_time())
    interpreter_receiver = fields.Char(string='Interpreter Receiver')
    street = fields.Char(string='Street',
                         default=lambda self: self._get_address('street'))
    street2 = fields.Char(string='Street2',
                          default=lambda self: self._get_address('street2'))
    zip = fields.Char(string='Zip',
                      change_default=True,
                      default=lambda self: self._get_address('zip'))
    city = fields.Char(string='City',
                       default=lambda self: self._get_address('city'))
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        default=lambda self: self._get_address('state_id'))
    country_id = fields.Many2one(
        'res.country', string='Country',
        default=lambda self: self._get_address('country_id'))
    interpreter_booking_ref = fields.Char(string='Booking Reference',
                                          readonly=True)
    interpreter_ref = fields.Char(string='Interpreter reference',
                                  readonly=True)
    interpreter_booking_status = fields.Char(string='Booking Status',
                                             readonly=True,
                                             compute='_compute_booking_status')
    # Internal booking status to hold certain data to be computed.
    _interpreter_booking_status = fields.Char(string='Technical Booking Status Internal',
                                              readonly=True,
                                              default=_('Not booked'))
    _interpreter_booking_status_2 = fields.Char(string='Booking Status Internal',
                                                readonly=True,
                                                default='0')
    interpreter_name = fields.Char(string='Interpreter Name',
                                   readonly=True)
    interpreter_phone = fields.Char(string='Interpreter Phone Number',
                                    readonly=True)
    interpreter_company = fields.Char(string='Interpreter Supplier Company',
                                      readonly=True)
    interpreter_contact_person = fields.Char(
        string='Interpreter Supplier Contact',
        readonly=True)
    interpreter_contact_phone = fields.Char(
        string='Interpreter Supplier Phone Number',
        readonly=True)

    interpreter_ka_nr = fields.Char(compute='_compute_ka_nr')

    def _compute_ka_nr(self):
        for record in self:
            perf_op = record.get_outplacement_value('performing_operation_id')
            record.interpreter_ka_nr = perf_op.ka_nr if perf_op else None

    @api.depends('_interpreter_booking_status',
                 '_interpreter_booking_status_2',
                 'interpreter_company')
    def _compute_booking_status(self):
        tech_statuses = {'1': _('Order received'),
                         '2': _('Delivered')}
        statuses = {'1': _('Order received'),
                    '2': _('No available interpreter'),
                    '3': _('Order received'),
                    '4': _('Interpreter Booked'),
                    '5': _('Cancelled by Interpreter'),
                    '6': _('Cancelled by AF')}
        for record in self:
            tech_status = record._interpreter_booking_status
            status = record._interpreter_booking_status_2
            if tech_status == '2':
                record.interpreter_booking_status = tech_statuses['2']
            elif (record.time_end
                  and record.time_end < datetime.datetime.now()
                  and tech_status != '2'
                  and status == '4'):
                record.interpreter_booking_status = _('Not delivered yet!')
            elif status in statuses:
                record.interpreter_booking_status = statuses[status]
            # Legacy
            elif record.interpreter_company and tech_status == '1':
                record.interpreter_booking_status = statuses['4']
            else:
                record.interpreter_booking_status = status

    def _get_end_time(self):
        """
        Calculate endtime by taking start time and add planned hours.
        """
        start_time = self._get_default_task_value('start_date')
        duration = self._get_default_task_value('planned_hours')
        if start_time and duration:
            return start_time + datetime.timedelta(hours=duration)

    def _get_address(self, field):
        """
        Get default address field from res.partner on performing
        operation.
        """
        perf_op = self._get_default_outplacement_value(
            'performing_operation_id')
        if perf_op and perf_op.partner_ids:
            partner = perf_op.partner_ids[0]
            try:
                return getattr(partner, field)
            except AttributeError:
                pass

    def _get_default_task_value(self, field_name):
        """
        Get Default values from parent task.
        """
        res_id = self.env.context.get('default_res_id')
        res_model = self.env.context.get('default_res_model')
        if res_model == 'project.task' and res_id:
            project_task = self.env[res_model].browse(res_id)
            if project_task:
                try:
                    return getattr(project_task, field_name)
                except AttributeError:
                    pass

    def _get_default_outplacement_value(self, field_name):
        """
        Get Default values from parent Outplacement.
        Used for loading default values at startup, use
        get_outplacement_value when calling from the outside.
        """
        res_id = self.env.context.get('default_res_id')
        res_model = self.env.context.get('default_res_model')
        if res_model == 'project.task' and res_id:
            project_task = self.env[res_model].browse(res_id)
            try:
                if project_task and project_task.outplacement_id:
                    return getattr(project_task.outplacement_id, field_name)
            except AttributeError:
                _logger.warn('Could not find field: {field_name}')

    @api.multi
    def get_outplacement_value(self, field_name):
        """
        Get a value from parent outplacement.
        """
        if self.res_model == 'project.task' and self.res_id:
            project_task = self.env[self.res_model].browse(self.res_id)
            try:
                if project_task.exists() and project_task.outplacement_id:
                    return getattr(project_task.outplacement_id, field_name)
            except AttributeError:
                _logger.warn('Could not find field: {field_name}')

    @api.multi
    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary or self.res_name,
            'default_description': self.note and tools.html2plaintext(
                self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
            'initial_date': self.date_deadline,
        }
        return action

    def action_feedback(self, feedback=False):
        '''
        Overriding the standard action feedback for interpreter messages.
        As the standard version takes height for that it may be more
        than one message we need to take height for it as well.
        '''
        interpreter_messages = self.filtered(lambda m: self.is_interpreter())
        other_messages = self - interpreter_messages
        if other_messages:
            result = super(MailActivity, other_messages).action_feedback(feedback)
        if interpreter_messages:
            message = self.env['mail.message']
            if feedback:
                self.write(dict(feedback=feedback))

            # Search for all attachments linked to the activities we
            # are about to unlink. This way, we can link them to the
            # message posted and prevent their deletion.
            attachments = self.env['ir.attachment'].search_read([
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
            ], ['id', 'res_id'])

            activity_attachments = defaultdict(list)
            for attachment in attachments:
                activity_id = attachment['res_id']
                activity_attachments[activity_id].append(attachment['id'])

            for activity in interpreter_messages:
                record = self.env[activity.res_model].browse(activity.res_id)
                record.message_post_with_view(
                    'mail.message_activity_done',
                    values={'activity': activity},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                    mail_activity_type_id=activity.activity_type_id.id,
                )

                activity_message = record.message_ids[0]
                message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
                if message_attachments:
                    message_attachments.write({
                        'res_id': activity_message.id,
                        'res_model': activity_message._name,
                    })
                    activity_message.attachment_ids = message_attachments
                message |= activity_message

            interpreter_messages.write({'active': False})
            return message.ids and message.ids[0] or False
        return result

    @api.model
    def create(self, vals):
        """Adding request to server in create."""
        order_interpreter = self.env.ref(
            'outplacement_order_interpreter.order_interpreter').id
        if vals['activity_type_id'] == order_interpreter:
            for field in ('time_start', 'time_end'):
                vals[field] = self.strip_seconds(vals[field])
            vals['date_deadline'] = vals['time_start']
        record = super(MailActivity, self).create(vals)
        if record.activity_type_id.id == order_interpreter:
            self.validate_booking_rules(record)
            self.make_request(record)
        return record

    def make_request(self, record=None):
        """Makes request to server with a booking."""
        record = record or self
        try:
            resp = self.env[
                'ipf.interpreter.client'].post_tolkbokningar(record)
        except Exception as e:
            _logger.exception(e)
        else:
            record.process_response(*resp)

    def validate_booking_rules(self, record):
        """Validate record against various rules in the portal."""
        start = record.time_start.replace(second=0)
        end = record.time_end.replace(second=0)
        if start <= datetime.datetime.now():
            raise UserError(_('Start time cannot be before now.'))
        if start >= end:
            raise UserError(_('Endtime is before start time'))
        time_diff = end - start
        # {rule_id: (minimum_minutes, increment_size, name)}
        rules = {'3': {'min': 60, 'increment': 30, 'name': 'onsite'},
                 '2': {'min': 30, 'increment': 15, 'name': 'phone'}}
        meeting = rules.get(record.interpreter_type[0].code, {})
        if not meeting:
            # No rule for this meeting type
            return True
        if not time_diff >= datetime.timedelta(minutes=meeting['min']):
            raise UserError(_('This type of booking needs to be atleast {min} '
                              'minutes long.').format(min=meeting['min']))
        increment = meeting['increment']
        if time_diff.seconds % (increment*60):
            raise UserError(_('Booking has to be an even '
                              '{} minutes segment.').format(increment))
        return True

    def strip_seconds(self, dt):
        """Remove seconds from a dt"""
        return f'{dt.rsplit(":", 1)[0]}:00'

    @api.multi
    def process_response(self, response, payload):
        """Process response from a interpreter booking."""
        # Note that calling code relies on that UserError is thrown when
        # wrong status is caught.
        msg = 'Failed to make booking'
        try:
            status_code = response.status_code
        except AttributeError:
            self._interpreter_booking_status = msg
            _logger.exception(msg)
            raise UserError(_('Unknown error making Interpreter booking'))
        if status_code == 200:
            self.interpreter_booking_ref = response.text
            self._interpreter_booking_status_2 = _('1')
            _logger.debug('Interpreter booking success.')
        elif status_code == 404:
            self._interpreter_booking_status = msg
            _logger.error('Check KA-Number and that address is correct.')
            _logger.error(response.text)
            _logger.error(payload)
            msg = _('Failed to book Interpreter, '
                    'please check KA-Number and address in request.\n')
            raise UserError(f'{msg}{json.loads(response.text)["message"]}')
        else:
            self._interpreter_booking_status = msg
            err_msg = (f'\n{msg}\n{_("Response text")}:\n{response.text}\n'
                       f'{_("Response status code")}:\n{response.status_code}')
            _logger.error(err_msg)
            _logger.error(payload)
            raise UserError(err_msg)

    @api.multi
    def update_activity(self, response):
        """
        Updates the activity with new status if it has been updated on
        server.
        """
        def change_tz(dt, tz='Europe/Stockholm'):
            # Tolkportalen gives times in swedish local time.
            if dt:
                tz = pytz.timezone(tz)
                dt = tz.localize(dt).astimezone(datetime.timezone.utc)
                # Making it naive again so that Odoo likes it.
                return dt.replace(tzinfo=None)
            return False

        if response.status_code not in (200,):
            _logger.warn('Failed to update interperator bookings with code: '
                         f'{response.status_code}')
            return
        data = json.loads(response.content.decode())
        self._interpreter_booking_status = str(
            data.get('tekniskStatusTypId', self._interpreter_booking_status))
        self._interpreter_booking_status_2 = str(
            data.get('statusTypId', self._interpreter_booking_status_2))
        self.interpreter_type = self.env["res.interpreter.type"].search([('code', '=', data.get('tolkTypId'))])  # noqa:E501
        self.interpreter_remote_type = self.env["res.interpreter.remote_type"].search([('code', '=', data.get('distanstolkTypId'))])  # noqa:E501
        self.time_start = change_tz(datetime.datetime.strptime(
            data.get('fromDatumTid'),
            '%Y-%m-%dT%H:%M:%S'))
        self.time_end = change_tz(datetime.datetime.strptime(
            data.get('tomDatumTid'),
            '%Y-%m-%dT%H:%M:%S'))
        address_obj = data.get('adress', {})
        self.street = address_obj.get('gatuadress')
        self.zip = address_obj.get('postnr')
        self.city = address_obj.get('ort')
        # state_id is not used, and its uncertain that code is the one
        # to be used.
        self.state_id = self.env['res.country.state'].search([('code', '=', address_obj.get('kommunkod'))], limit=1) or False  # noqa:E501
        self.interpreter_language = self.env["res.interpreter.language"].search([('code', '=', data.get('tolksprakId'))])  # noqa:E501
        self.interpreter_gender = self.env["res.interpreter.gender_preference"].search([('code', '=', data.get('tolkkonID'))])  # noqa:E501
        self.interpreter_ref = data.get('tolkId')
        self.interpreter_name = data.get('tolkNamn')
        self.interpreter_phone = data.get('tolkTelefonnummer')
        self.interpreter_company = data.get(
            'tolkLeverantorVerksamhetsnamn')
        supplier_obj = data.get('tolkLeverantorKontaktperson', {})
        self.interpreter_contact_person = supplier_obj.get('namn')
        self.interpreter_contact_phone = supplier_obj.get(
            'telefonnummer')
        # Force computation if time has passed
        if self.time_end and self.time_end < datetime.datetime.now():
            self._compute_booking_status()

    @api.model
    def cron_order_interpreter(self):
        """Cron job to check booking status."""
        ipf_client = self.env['ipf.interpreter.client']
        if not ipf_client.is_params_set():
            return
        for activity in self.env['mail.activity'].search([]):
            if not activity.is_interpreter():
                continue
            ref = activity.interpreter_booking_ref
            perf_op = activity.get_outplacement_value(
                'performing_operation_id')
            ka_nr = perf_op.ka_nr if perf_op else None
            if not (ka_nr and ref):
                continue
            _logger.debug(f'Checking status on booking with ref: {ref}')
            response = ipf_client.get_tolkbokningar_id(ref, ka_nr)
            activity.update_activity(response)

    @api.multi
    def activity_format(self):
        """Add is_interpreter_order field to activity"""
        activities = super().activity_format()
        type_id = self.env['ir.model.data'].xmlid_to_res_id(
            'outplacement_order_interpreter.order_interpreter')
        for activity in activities:
            if activity['activity_type_id'][0] == type_id:
                activity['is_interpreter_order'] = True
        return activities

    @api.multi
    def interpreter_cancel_booking(self):
        """
        Runs after user presses Yes in dialog to remove interpreter
        bookings.
        """
        author = self.env['res.users'].browse(self.env.uid).partner_id.id
        ref = self.interpreter_booking_ref
        message = _('<p>Interpreter booking with ref: {ref} canceled<p>')
        message_id = self.env['mail.message'].create({
            'body': message.format(ref=ref),
            'subject': f"{_('Cancled Interpreter booking')}",
            'author_id': author,
            'res_id': self.res_id,
            'model': self.res_model,
            })
        _logger.info(f'{author} {message_id.body}')
        self.active = False

    @api.model
    def is_interpreter(self, obj=None):
        """Checks if activity is of order_interpreter type."""
        obj = obj or self
        order_interpreter = self.env.ref(
            'outplacement_order_interpreter.order_interpreter').id
        return obj.activity_type_id.id == order_interpreter
