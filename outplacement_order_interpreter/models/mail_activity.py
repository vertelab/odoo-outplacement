# -*- coding: utf-8 -*-

import datetime
import json
import logging
import traceback

from odoo import api, models, fields, tools

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    interpreter_language = fields.Many2one(
        comodel_name='res.interpreter.language',
        string='Interpreter Language',
        default=lambda self: self._get_default_outplacement_value(
            'interpreter_language'))
    interpreter_gender_preference = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('no_preference', 'No preference')],
        string="Gender Preference",
        default=lambda self: self._get_default_outplacement_value(
            'interpreter_gender_preference'))
    location_type = fields.Selection([
        ('on_premise', 'On premise'),
        ('telephone', 'Telephone')],
        string='Location',
        default=lambda self: self._get_location_type())
    time_start = fields.Datetime(
        'Start Time',
        default=lambda self: self._get_default_task_value('start_date'))
    time_end = fields.Datetime(string='End Time',
                               default=lambda self: self._get_end_time())
    phone = fields.Char()
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
    interpeter_booking_ref = fields.Char('Booking Reference')
    Interpreteter_booking_status = fields.Char('Booking Status')
    department_id = fields.Many2one('hr.department', 'Department')

    def _get_end_time(self):
        """
        Calculate endtime by taking start time and add planned hours.
        """
        start_time = self._get_default_task_value('start_date')
        duration = self._get_default_task_value('planned_hours')
        if start_time and duration:
            return start_time + datetime.timedelta(hours=duration)

    def _get_location_type(self):
        """Get location type from outplacement."""
        remote = self._get_default_outplacement_value(
            'meeting_remote') == 'yes'
        return 'telephone' if remote else 'on_premise'

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
        Get Default values from task.
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
        """
        res_id = self.env.context.get('default_res_id')
        res_model = self.env.context.get('default_res_model')
        if res_model == 'project.task' and res_id:
            project_task = self.env[res_model].browse(res_id)
            try:
                if project_task and project_task.outplacement_id:
                    return getattr(project_task.outplacement_id, field_name)
            except AttributeError:
                pass

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
                _logger.error(e)
                _logger.error(traceback.format_exc())
                resp = None
            if resp:
                try:
                    record.processing_response(resp)
                except Exception as e:
                    _logger.error(e)
                    _logger.error(traceback.format_exc())
        return record

    @api.model
    def processing_response(self, response):
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            self.booking_ref = data.get('tolkbokningId')

    # ToDo: Poll Tolkportalen to get status of open orders and update
    #       status.
    @api.model
    def cron_order_interpreter(self):
        pass
