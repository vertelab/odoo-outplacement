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
                                    params=params)

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
        headers = {
            'x-amf-mediaType': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "AF-SystemId",
            'AF-EndUserId': "AF-EndUserId",
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
        if not payload:
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

        url = self.get_url('v1/gemensam-planering')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)
