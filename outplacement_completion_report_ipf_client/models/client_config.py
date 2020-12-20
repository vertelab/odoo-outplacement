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

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

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
        ('u1', 'U1'),
        ('i1', 'I1'),
        ('t1', 'IT'),
        ('t2', 'T2'),
        ('prod', 'PROD'),
    ], string='Environment',
        default='u1',
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
            self.env["ir.config_parameter"].sudo().get_param("api_ipf.ipf_system_id")
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

    def test_post_report(self):
        payload = {
            "utforande_verksamhets_id": "10009858",
            "avrops_id": "A000000398768",
            "genomforande_referens": "100000123",
            "ordernummer": "MEET-1",
            "personnr": "197608277278",
            "unikt_id": "1321",
            "deltagare": {
                "fornamn": "John",
                "efternamn": "Doe",
                "deltog_per_distans": "yes"
            },
            "inskickad_datum": "2020-08-20",
            "status": "SENT",
            "innehall": [
                {
                    "aktivitets_id": "1",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test"
                },
                {
                    "aktivitets_id": "2",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 2"
                },
                {
                    "aktivitets_id": "3",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 3"
                },
                {
                    "aktivitets_id": "4",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 4"
                },
                {
                    "aktivitets_id": "5",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 5"
                },
                {
                    "aktivitets_id": "6",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 6"
                },
                {
                    "aktivitets_id": "7",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 7"
                },
                {
                    "aktivitets_id": "8",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 8"
                },
                {
                    "aktivitets_id": "9",
                    "aktivitets_namn": "KVL",
                    "beskrivning": "test 9"
                }
            ]
        }

        response = self.post_report(payload)
        print(response.text)

    @api.model
    def get_api(self):
        return self.search([], limit=1)

    @api.model
    def post_request(self, outplacement, res_joint_planning_af_recordset):
        res_join = res_joint_planning_af_recordset
        api = self.get_api()
        if 'department_ref' in outplacement.department_id:
            dep_id = outplacement.department_id.department_ref
        else:
            dep_id = outplacement.department_id.ka_ref
        payload = {
            "utforande_verksamhets_id": dep_id,
            "avrops_id": outplacement.name,
            "genomforande_referens": outplacement.order_id.origin,
            "ordernummer": outplacement.order_id.name,
            "personnr": outplacement.partner_id.company_registry,
            "unikt_id": "1321",
            "deltagare": {
                "fornamn": outplacement.partner_id.firstname,
                "efternamn": outplacement.partner_id.lastname,
                "deltog_per_distans": outplacement.meeting_remote
            },
            "inskickad_datum": str(outplacement.jp_sent_date),
            "innehall": []
        }
        for planned in self.env['res.joint_planning'].search([('send2server','=',True)],order=sequence):
            task = outplacement.task_ids.filtered(lambda t: t.activity_id = planned.activity_id)
            payload['innehall'].append({
                'aktivitets_id': planned.activity_id,
                'aktivitets_namn': task.activity_name if task else planned.activity_name,
                'beskrivning': task.description if task else '',
            })
        api.post_report(payload)
