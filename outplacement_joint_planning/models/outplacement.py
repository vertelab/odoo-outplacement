# -*- coding: UTF-8 -*-

################################################################################
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
################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date

import logging
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    jp_sent_date = fields.Date(string="Joint Planning Sent Date",
                               track_visibility='onchange',
                               help="Latest Sent Date for Joint Planning")

    
    def _compute_task_count(self):
        for outplacement in self:
            outplacement.task_count = self.env['project.task'].search_count([('outplacement_id','=',outplacement.id)])
    task_count = fields.Integer(compute='_compute_task_count', string="Task Count")

    @api.model
    def send_gp_to_bar(self):
        client = self.env['ipf.completion_report.client.config'].search(
            [], limit=1)
        if not client:
            raise ValidationError(
                _('Please, configure the configuration to send this report.'))

        for outplacement in self:
            outplacement.jp_sent_date = date.today()
            joint_plannings = self.env['res.joint_planning'].search([])
            client.post_request(outplacement, joint_plannings)

