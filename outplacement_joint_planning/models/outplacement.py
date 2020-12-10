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


class Outplacement(models.Model):
    _inherit = "outplacement"

    jp_sent_date = fields.Date(string="Log on change",
                               track_visibility='onchange')

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
            joint_planning_data = [{"aktivitets_id": joint_planning.activity_id,
                                    "aktivitets_namn": joint_planning.task_type,
                                    "beskrivning": joint_planning.name}
                                   for joint_planning in joint_plannings]
            payload = {
                "utforande_verksamhets_id": "10009858",
                "avrops_id": "A000000398768",
                "genomforande_referens": "100000123",
                "ordernummer": "MEET-1",
                "personnr": "197608277278",
                "unikt_id": "1321",
                "deltagare": {
                    "fornamn": "John",  # outplacement.user_id.partner_id.firstname
                    "efternamn": "Doe",  # outplacement.user_id.partner_id.lastname
                    "deltog_per_distans": "yes"
                },
                "inskickad_datum": "2020-08-20",
                "status": "SENT",
                "innehall": joint_planning_data
            }
            from pprint import pprint
            pprint(payload)
            client.post_report(payload)
