# -*- coding: UTF-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import datetime
import json
import logging
from datetime import date, timedelta
from odoo.exceptions import ValidationError, UserError, Warning

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    jp_sent_date = fields.Date(string="Joint Planning Sent Date",
                               track_visibility='onchange',
                               help="Latest Sent Date for Joint Planning")
    time_to_submit_jp = fields.Boolean(compute="compute_time_to_submit_jp", store=True)

    def date_by_adding_business_days(self, from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday = 6
                continue
            business_days_to_add -= 1
        return current_date

    @api.depends('jp_sent_date', 'service_start_date')
    def compute_time_to_submit_jp(self):
        today = datetime.date.today()
        for rec in self:
            if rec.service_start_date and not rec.jp_sent_date:
                next_5_days = self.date_by_adding_business_days(rec.service_start_date, 5)
                if today > next_5_days:
                    rec.time_to_submit_jp = True

    def cron_check_joint_planning_submit_time(self):
        today = datetime.date.today()
        for rec in self.search([('service_start_date', '!=', False), ('jp_sent_date', '=', False)]):
            next_5_days = self.date_by_adding_business_days(rec.service_start_date, 5)
            if today > next_5_days:
                rec.time_to_submit_jp = True

    def _compute_task_count(self):
        for outplacement in self:
            outplacement.task_count = self.env['project.task'].search_count(
                [('outplacement_id', '=', outplacement.id)])

    task_count = fields.Integer(
        compute='_compute_task_count', string="Task Count")

    @api.one
    def send_gp_to_bar(self):
        if self.date_by_adding_business_days(self.service_start_date, 5) > date.today():
            raise ValidationError(_("You are not allowed to send GP until the 6th working day "
                                    "since the service start date"))
        client = self.env['ipf.completion_report.client.config'].search(
            [], limit=1)
        if not client:
            raise ValidationError(
                _('Please, configure the configuration to send this report.'))
        email_to = self.env['ir.config_parameter'].sudo().get_param('system_parameter_to_send_api_error')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        model_obj = self.env['ir.model.data']
        for outplacement in self:
            if 'department_ref' in outplacement.performing_operation_id:
                dep_id = outplacement.performing_operation_id.ka_nr
            else:
                dep_id = outplacement.performing_operation_id.ka_nr

            if not outplacement.meeting_remote:
                raise Warning(_("Meeting type for outplacement not set."))
            if not dep_id:
                raise Warning(_("KA nr. not set on performing operation."))

            joint_plannings = self.env['res.joint_planning'].search([])
            try:
                outplacement.jp_sent_date = date.today()
                response = client.post_request(outplacement, joint_plannings)
                if response and response.status_code != 201:
                    error_msg = str(response.status_code) + " - " + response.reason
                    error_msg += "\n" + str(json.loads(response.content))
                    _logger.error("Something went wrong with sending GP to BÄR Outplacement %s. Getting %s Response" % (
                    outplacement.name, error_msg))
                    if email_to:
                        menu_id = model_obj.get_object_reference('outplacement', 'menu_outplacement')[1]
                        action_id = model_obj.get_object_reference('outplacement', 'outplacement_action')[1]
                        url = base_url + "/web?#id=" + str(
                            outplacement.id) + "&view_type=form&model=outplacement&menu_id=" + str(
                            menu_id) + "&action=" + str(action_id)
                        template = self.env.ref(
                            'outplacement_joint_planning.email_template_to_report_error_on_jp')
                        mail = template.with_context(email_to=email_to, url=url,
                                                     error_msg=str(error_msg)).send_mail(outplacement.id,
                                                                                         force_send=True)
                        mail = self.env['mail.mail'].browse(mail)
                        mail.mail_message_id.body = (_('There was an error when sending the joint planning.'
                                                       ' It has been reported to Service desk and will be handled. '))
            except Exception as e:
                _logger.error(
                    "Something went wrong with sending GP to BÄR Outplacement %s. %s" % (outplacement.name, str(e)))
                if email_to:
                    menu_id = model_obj.get_object_reference('outplacement', 'menu_outplacement')[1]
                    action_id = model_obj.get_object_reference('outplacement', 'outplacement_action')[1]
                    url = base_url + "/web?#id=" + str(
                        outplacement.id) + "&view_type=form&model=outplacement&menu_id=" + str(
                        menu_id) + "&action=" + str(action_id)
                    template = self.env.ref(
                        'outplacement_joint_planning.email_template_to_report_error_on_jp')
                    mail = template.with_context(email_to=email_to, url=url,
                                                 error_msg=str(e)).send_mail(outplacement.id, force_send=True)
                    mail = self.env['mail.mail'].browse(mail)
                    mail.mail_message_id.body = (_('There was an error when sending the joint planning.'
                                                   ' It has been reported to Service desk and will be handled. '))
