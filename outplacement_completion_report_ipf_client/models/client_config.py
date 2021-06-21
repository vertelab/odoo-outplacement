# -*- coding: UTF-8 -*-

########################################################################
#                                                                      #
#    OpenERP, Open Source Management Solution                          #
#    Copyright (C) 2019 N-Development (<https://n-development.com>).   #
#                                                                      #
#    This program is free software: you can redistribute it and/or     #
#    modify it under the terms of the GNU Affero General Public        #
#    License as published by the Free Software Foundation, either      #
#    version 3 of the License, or (at your option) any later version.  #
#                                                                      #
#    This program is distributed in the hope that it will be useful,   #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of    #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
#    GNU Affero General Public License for more details.               #
#                                                                      #
#    You should have received a copy of the GNU Affero General Public  #
#    License along with this program.  If not, see                     #
#    <http://www.gnu.org/licenses/>.                                   #
#                                                                      #
########################################################################

import json
import logging
import requests
import uuid
from odoo.exceptions import Warning
from odoo.tools import pycompat

from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _name = 'ipf.completion_report.client.config'
    _description = 'Completion report ipf client'
    _rec_name = 'url'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[
        ('U1', 'U1'),
        ('I1', 'I1'),
        ('T1', 'IT'),
        ('T2', 'T2'),
        ('PROD', 'PROD'),
    ], string='Environment',
        default='U1',
        required=True)
    request_history_ids = fields.One2many(
        'ipf.completion_report.request.history',
        'config_id',
        string='Requests')

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

        response = requests.request(method=method,
                                    url=url,
                                    data=payload,
                                    headers=headers,
                                    params=params,
                                    verify=False)

        self.create_request_history(method=method,
                                    url=url,
                                    response=response,
                                    payload=payload,
                                    headers=headers,
                                    params=params)

        return response

    def create_request_history(self, method, url, response, payload=None,
                               headers=None, params=None):
        values = {
            'config_id': self.id,
            'method': method,
            'url': url,
            'payload': payload,
            'request_headers': headers,
            'response_headers': response.headers,
            'params': params,
            'response_code': response.status_code,
        }
        try:
            values.update(message=json.loads(response.content))
        except json.decoder.JSONDecodeError:
            pass
        self.env['ipf.completion_report.request.history'].create(values)

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        ipf_system_id = (
            self.env["ir.config_parameter"].sudo().get_param(
                "api_ipf.ipf_system_id")
        )
        headers = {
            'Content-Type': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': ipf_system_id,
            'AF-EndUserId': "*sys*",
            'AF-Environment': self.environment,
        }
        return headers

    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url + path
        else:
            url = self.url + '/' + path
        return url

    def post_report(self, payload):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        url = self.get_url('v1/gemensam-planering')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        return response

    @api.model
    def get_api(self):
        return self.search([], limit=1)

    @api.model
    def post_request(self, outplacement, res_joint_planning_af_recordset):
        api = self.get_api()
        if 'department_ref' in outplacement.performing_operation_id:
            dep_id = outplacement.performing_operation_id.ka_nr
            _logger.info("using department_ref %s"
                         % outplacement.performing_operation_id.ka_nr)
        else:
            dep_id = outplacement.performing_operation_id.ka_nr
            _logger.info("using ka_ref %s"
                         % outplacement.performing_operation_id.ka_nr)

        if not outplacement.meeting_remote:
            raise Warning(_("Meeting type for outplacement not set."))
        if not dep_id:
            raise Warning("KA nr. not set on performing operation.")

        # Add version handling to unik_id (unique id)
        unikt_id = outplacement.uniq_ref.split('_')
        if len(unikt_id) == 1:
            unikt_id = unikt_id[0] + '_0'
        else:
            unikt_id = f'{unikt_id[0]}_{int(unikt_id[1]) + 1}'
        outplacement.write({'uniq_ref': unikt_id})

        payload = {
            "utforande_verksamhets_id": str(dep_id),
            "avrops_id": "A000000000000",
            "genomforande_referens": outplacement.order_id.origin,
            "ordernummer": outplacement.order_id.name,
            "personnr": outplacement.partner_id.social_sec_nr.replace('-', ''),
            "unikt_id": unikt_id,
            "deltagare": {
                "fornamn": outplacement.partner_id.firstname,
                "efternamn": outplacement.partner_id.lastname,
                "deltog_per_distans": outplacement.meeting_remote
            },
            "inskickad_datum": str(outplacement.jp_sent_date),
            "status": str(outplacement.stage_id.sequence),
            "ofullstandig": "true" if outplacement.incomplete else "false",
            "sent_inskickad": "true" if outplacement.late else "false",
            "innehall": []
        }
        # As BÄR only accept certain IDs and only in the correct order
        # the activites are matched towards res.joint_planning and only
        # those marked as send2server is sent in the correct order.
        for planned in self.env['res.joint_planning'].search(
                [('send2server', '=', True)], order="sequence"):
            _logger.debug("send2server for %s %s" % (planned.activity_id,
                                                     planned.send2server))
            task = outplacement.task_ids.filtered(
                lambda t: t.activity_id == planned.activity_id)
            payload['innehall'].append({
                'aktivitets_id': planned.activity_id,
                'aktivitets_namn': (task.activity_name
                                    if task else planned.name),
                'beskrivning': task.description if task else '',
            })
        _logger.warn(payload)
        api.post_report(payload)

    def test_post_report(self):
        payload = {
            "utforande_verksamhets_id": "10011119",
            "avrops_id": "A000000428847",
            "genomforande_referens": "100003568",
            "ordernummer": "MEET-1",
            "personnr": "199910103028",
            "unikt_id": "1111-3",
            "deltagare": {
                "fornamn": "John",
                "efternamn": "Doe",
                "deltog_per_distans": "yes"
            },
            "inskickad_datum": "2020-11-25",
            "status": "10",
            "ofullstandig": "true",
            "sent_inskickad": "false",
            "innehall": [
                {
                    "aktivitets_id": "176",
                    "aktivitets_namn": "Val och framtidsplanering - "
                                       "deltagarens karriärplan",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "177",
                    "aktivitets_namn": "Individuella "
                                       "karriärsvägledningssamtal",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "178",
                    "aktivitets_namn": "Stöd till att bli antagen till "
                                       "kommunens insatser",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "179",
                    "aktivitets_namn": "Studiebesök utbildningsanordnare",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "180",
                    "aktivitets_namn": "Studiebesök arbetsplatser",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "181",
                    "aktivitets_namn": "Möte med förebilder.",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "182",
                    "aktivitets_namn": "Kunskap om arbetsmarknad, "
                                       "utbildningsvägar, studiefinansiering, "
                                       "omvärldsbev.",
                    "beskrivning": "Coach's comment"
                }
            ]
        }

        response = self.post_report(payload)
        print(response.text)
