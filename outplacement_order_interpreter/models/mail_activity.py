# -*- coding: utf-8 -*-

import datetime
import json
import logging

from odoo import api, models, fields, tools

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

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
        string='Interpreter Type',)
    interpreter_remote_type = fields.Many2one(
        comodel_name='res.interpreter.remote_type',
        string='Interpreter Remote Type')
    time_start = fields.Datetime(
        'Start Time',
        default=lambda self: self._get_default_task_value('start_date'))
    time_end = fields.Datetime(string='End Time',
                               default=lambda self: self._get_end_time())
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
    interpreter_booking_ref = fields.Char(string='Booking Reference')
    interpreteter_booking_status = fields.Char(string='Booking Status',
                                               readonly=True,
                                               default='Not booked')
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
                if project_task and project_task.outplacement_id:
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

    @api.model
    def create(self, vals):
        record = super(MailActivity, self).create(vals)
        order_interpreter = self.env.ref(
            'outplacement_order_interpreter.order_interpreter').id
        if record.activity_type_id.id == order_interpreter:
            try:
                resp = self.env[
                    'ipf.interpreter.client'].post_tolkbokningar(record)
            except Exception as e:
                _logger.exception(e)
            else:
                record.process_response(resp, record)
        return record

    @api.model
    def process_response(self, response, record):
        if response and response.status_code == 200:
            data = json.loads(response.content.decode())
            record.booking_ref = data.get('tolkbokningId')
            record.interpreteter_booking_status = 'Request sent'
        else:
            msg = 'Failed to make booking'
            record.interpreteter_booking_status = msg
            _logger.error(f'\n{msg}\nResponse text:\n{response.text}\n'
                          f'Response status code:\n{response.status_code}')

    @api.model
    def update_activity(self, activity_obj, response):
        if response.status_code not in (200,):
            _logger.warn('Failed to update interperator bookings with code: '
                         f'{response.status_code}')
            return
        data = json.loads(response.content.decode())
        activity_obj.interpreteter_booking_status = data.get(
            'tekniskStatusTypId')
        activity_obj.interpreter_type = data.get('tolkTypId')
        activity_obj.interpreter_remote_type = data.get('distanstolkTypId')
        activity_obj.time_start = datetime.datetime.fromtimestamp(
            data.get('fromDatumTid'))
        activity_obj.time_end = datetime.datetime.fromtimestamp(
            data.get('toDatumTid'))
        address_obj = data.get('address')
        activity_obj.street = address_obj.get('adress')
        activity_obj.zip = address_obj.get('postnr')
        activity_obj.city = address_obj.get('ort')
        activity_obj.state_id = address_obj.get('kommunkod')
        activity_obj.interpreter_language = data.get('tolksprakId')
        activity_obj.interpreter_gender = data.get('tolkkonID')
        activity_obj.interpreter_ref = data.get('tolkId')
        activity_obj.interpreter_name = data.get('tolkNamn')
        activity_obj.interpreter_phone = data.get('tolkTelefonnummer')
        activity_obj.interpreter_company = data.get(
            'tolkLeverantorVerksamhetsnamn')
        supplier_obj = data.get('tolkLeverantorKontaktperson')
        activity_obj.interpreter_contact_person = supplier_obj('namn')
        activity_obj.interpreter_contact_phone = supplier_obj('telefonnummer')

    @api.model
    def cron_order_interpreter(self):
        ipf_client = self.env['ipf.interpreter.client']
        if not ipf_client.is_params_set():
            return
        for activity in self.env['mail.activity'].search([]):
            if not activity.is_interpreter():
                continue
            ref = activity.interpreter_booking_ref
            perf_op = activity.get_outplacement_value(
                'performing_operation_id')
            if not perf_op:
                continue
            ka_nr = perf_op.ka_nr
            response = ipf_client.get_tolkbokningar_id(ref, ka_nr)
            self.update_activity(activity, response)

    @api.multi
    def activity_format(self):
        activities = super().activity_format()
        type_id = self.env['ir.model.data'].xmlid_to_res_id(
            'outplacement_order_interpreter.order_interpreter')
        for activity in activities:
            if activity['activity_type_id'][0] == type_id:
                activity['is_interpreter_order'] = True
        return activities

    @api.multi
    def interpreter_cancel_booking(self):
        return

    @api.model
    def is_interpreter(self, obj=None):
        obj = obj or self
        order_interpreter = self.env.ref(
            'outplacement_order_interpreter.order_interpreter').id
        return obj.activity_type_id.id == order_interpreter

    @api.model
    def deliver_interpreter(self):
        if not self.is_interpreter():
            # ToDo: Add functionality here.
            return
