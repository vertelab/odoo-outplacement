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


import logging
from datetime import date, timedelta
from odoo.exceptions import ValidationError
import datetime
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

    def date_by_adding_business_days(self, from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:
                continue
            business_days_to_add -= 1
        return current_date

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

        for outplacement in self:
            outplacement.jp_sent_date = date.today()
            joint_plannings = self.env['res.joint_planning'].search([])
            client.post_request(outplacement, joint_plannings)
