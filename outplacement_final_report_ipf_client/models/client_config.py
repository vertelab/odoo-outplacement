# -*- coding: UTF-8 -*-

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _name = 'ipf.final_report.client.config'
    _description = 'Final report ipf client'
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
        'ipf.final_report.request.history',
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
        self.env['ipf.final_report.request.history'].create(values)

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
        url = self.get_url('v1/slutredovisning')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        return response

    def test_post_report(self):
        payload = {
            "utforande_verksamhets_id": "10011119",
            "avrops_id": "A000000428847",
            "genomforande_referens": "100003568",
            "ordernummer": "MEET-1",
            "personnr": "199910103028",
            "unikt_id": "1421",
            "inskickad_datum": "2020-12-22",
            "rapportering_datum": "2020-12-22",
            "status": "10",
            "sent_inskickad":"false",
            "deltagare": {
                "fornamn": "testperson",
                "efternamn": "testson",
                "deltog_per_distans": "false"
            },
            "ansvarig_handledare": {
                "fornamn": "John",
                "efternamn": "Doe",
                "signatur": "fritext"
            },
            "innehall": [
                {
                    "aktivitets_id": "176",
                    "aktivitets_namn": "Val och framtidsplanering - deltagarens karriärplan",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "177",
                    "aktivitets_namn": "Individuella karriärsvägledningssamtal",
                    "beskrivning": "Coach's comment"
                },
                {
                    "aktivitets_id": "178",
                    "aktivitets_namn": "Stöd till att bli antagen till kommunens insatser",
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
                    "aktivitets_namn": "Kunskap om arbetsmarknad, utbildningsvägar, studiefinansiering, omvärldsbev.",
                    "beskrivning": "Coach's comment"
                }
                ],
            "avbrott": "true",
            "ofullstandig": "false",
            "huvudmal": {
                "yrkesomrade": "Hotell & Restaurang",
                "yrke": "Kock",
                "arbetsuppgifter_beskrivning": "Lagar mat",
                "val_av_huvudmal_motivering": "Annat",
                "fritext": "Används vid val_av_huvudmal_motivering Annat",
                "steg": [{
                    "typ": "Studera",
                    "kompletterande_insats": {
                        "typ": "Studiemotiverande insats"
                    },
                    "namn": "",
                    "niva": "",
                    "startdatum": "2020-12-22",
                    "slutdatum": "2020-12-22"
                }]
            },
            "alternativ_mal": {
                "yrkesomrade": "Hotell & Restaurang",
                "yrke": "Kock",
                "arbetsuppgifter_beskrivning": "Lagar mat",
                "val_av_alternativ_mal_motivering": "Matchar deltagarens intressen",
                "steg": [{
                "typ": "Studera",
                "namn": "",
                "niva": "",
                "startdatum": "2020-12-22",
                "slutdatum": "2020-12-22"
                }]
            },
            "studiebesok": [{
                "namn": "utbildningssamordnare",
                "typ": "studieinriktning",
                "motivering": "fritext"
            }],
            "hinder": {
                "orsak_typ": "Annat",
                "motivering": "Fritext, används vid orsak_typ Annat"
            }
        }

        response = self.post_report(payload)
        print(response.text)

    @api.model
    def get_api(self):
        return self.search([], limit=1)

    @api.model
    def post_request(self, outplacement):
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
            "unikt_id": outplacement.uniq_ref,
            "inskickad_datum": str(outplacement.jp_sent_date),
            "rapportering_datum": outplacement.report_date, 
            "status": outplacement.status,
            "sent_inskickad": outplacement.late, 
            "innehall": [], #filled with data below
            "avbrott": outplacement.interruption, 
            "ofullstandig": outplacement.incomplete,
            "studiebesok": [], #filled with data below
        }
        if outplacement.partner_id:
            payload["deltagare"] = {
                "fornamn": outplacement.partner_id.firstname,
                "efternamn": outplacement.partner_id.lastname,
                "deltog_per_distans": outplacement.meeting_remote
            },
        if outplacement.employee_id:
            payload["ansvarig_handledare"] = {
                "fornamn": outplacement.employee_id.firstname,
                "efternamn": outplacement.employee_id.lastname,
            }
            if outplacement.employee_id.user_id:
                payload["ansvarig_handledare"]["signatur"] = outplacement.employee_id.user_id.login
        if outplacement.obstacle_id:
            payload["hinder"] = {
                "orsak_typ": outplacement.obstacle_id.reason,
                "motivering": outplacement.obstacle_id.motivation 
            }
        goal_id = outplacement.main_goal_id
        if goal_id:
            payload["huvudmal"] = { 
                "arbetsuppgifter_beskrivning": goal_id.job_description,
                "val_av_huvudmal_motivering": goal_id.motivation, #new field?
                "fritext": goal_id.free_text, #new field?
                "steg": []
            }
            if goal_id.field_of_work_id:
                payload["huvudmal"]["yrkesomrade"] = goal_id.field_of_work_id

            if goal_id.job_id:
                payload["huvudmal"]["yrke"] = goal_id.job_id

            for step_id in goal_id:
                step = {
                    "typ": step_id.step_type,
                    "namn": step_id.name,
                    "niva": step_id.level,
                    "startdatum": step_id.start_date,
                    "slutdatum": step_id.end_date
                }
                step["kompletterande_insats"] = {
                    "typ": step_id.complementing_effort_type,
                    "fritext": step_id.complementing_effort_description
                }
                payload['huvudmal']['steg'].append(step)
        goal_id = outplacement.alternative_goal_id
        if goal_id:
            payload["alternativ_mal"] = { 
                "arbetsuppgifter_beskrivning": goal_id.job_description,
                "val_av_huvudmal_motivering": goal_id.motivation, #new field?
                "fritext": goal_id.free_text, #new field?
                "steg": []
            }
            if goal_id.field_of_work_id:
                payload["alternativ_mal"]["yrkesomrade"] = goal_id.field_of_work_id

            if goal_id.job_id:
                payload["alternativ_mal"]["yrke"] = goal_id.job_id

            for step_id in goal_id:
                step = {
                    "typ": step_id.step_type,
                    "namn": step_id.name,
                    "niva": step_id.level,
                    "startdatum": step_id.start_date,
                    "slutdatum": step_id.end_date
                }
                step["kompletterande_insats"] = {
                    "typ": step_id.complementing_effort_type,
                    "fritext": step_id.complementing_effort_description
                }
                payload['alternativ_mal']['steg'].append(step)
               
        for planned in self.env['res.joint_planning'].search([('send2server','=',True)],order=sequence):
            task = outplacement.task_ids.filtered(lambda t: t.activity_id == planned.activity_id)
            payload['innehall'].append({
                'aktivitets_id': planned.activity_id,
                'aktivitets_namn': task.activity_name if task else planned.activity_name,
                'beskrivning': task.description if task else '',
            })
        for study_visit in outplacement.study_visit_ids:
            payload['studiebesok'].append({
                "namn": study_visit.name,
                "typ": study_visit.visit_type,
                "motivering": study_visit.reasoning 
            })
        return api.post_report(payload)
