# -*- coding: UTF-8 -*-

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

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
        ('T1', 'T1'),
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
            "genomforande_referens": "100003568",
            "ordernummer": "MEET-1",
            "personnummer": "199910103028",
            "unikt_id": "1421",
            "inskickad_datum": "2020-12-22",
            "rapportering_datum": "2020-12-22",
            "status": "10",
            "sent_inskickad": "false",
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
            "avbrott": "true",
            "ofullstandig": "false",
            "huvudmal": {
                "yrkesomrade": "Hotell & Restaurang",
                "yrke": "Kock",
                "arbetsuppgifter_beskrivning": "Lagar mat",
                "val_av_huvudmal_motivering": [
                    {
                        "typ": "Matchar deltagarens intressen"
                    },
                    {
                        "typ": "Annat",
                        "fritext": "Används vid val_av_huvudmal_motivering" 
                    }
                ],
                "steg": [
                    {
                    "typ": "Studera reguljär utbildning", 
                        # Studera reguljär utbildning 
                        #Lämpliga kompletterande insatser
                        # Annat
                    "namn": "",
                    "niva": "",
                    "startdatum": "2020-12-22",
                    "slutdatum": "2020-12-22"
                    },
                    {
                    "typ": "Lämpliga kompletterande insatser",
                    "kompletterande_insats": {   # This is displayed when "Lämpliga kompletterande insatser" is selected in "Typ"
                    "typ": "Studiemotiverande insats",
                        #Studiemotiverande insats
                        #Rusta inför arbete
                        #Matcha till arbete
                        #Utreda arbetsförmågan
                        #Delta i en arbetsmarknadsutbildning/Praktik/Validering
                        #Svenskastudier inom valt område
                        #Översättning av betyg
                        #Bedömning och komplettering av utländsk utbildning
                        #Annat
                    "fritext":"text goes here for Annat" # If "Annat" is selected in "Typ"
                    },
                    "namn": "",
                    "niva": "",
                    "startdatum": "2020-12-22",
                    "slutdatum": "2020-12-22"
                }, 
                {
                    "typ": "Annat",
                    "fritext":"Only sent when it is 'Annat'in Typ under steg object",
                    "namn": "Används vid val_av_huvudmal_motivering Annat",
                    "niva": "Används vid val_av_huvudmal_motivering Annat",
                    "startdatum": "2020-12-22",
                    "slutdatum": "2020-12-22"
                }

                ]
            },
            "alternativt_mal": {
                "yrkesomrade": "Hotell & Restaurang",
                "yrke": "Kock",
                "arbetsuppgifter_beskrivning": "Lagar mat",
                "val_av_alternativt_mal_motivering": [
                    {
                        "typ": "Matchar deltagarens intressen"
                    }
                ],
                "steg": [{
                    "typ": "Studera reguljär utbildning",
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
            "kompletterande_information": {
                "fraga": "komm_info",
                "svar": "komm_info_03"
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
        if outplacement.performing_operation_id:
            perf_op_id = outplacement.performing_operation_id.ka_nr
        elif outplacement.interruption:
            perf_op_id = ""
        else:
            raise ValidationError(_("Performing operation needs to be set to send final report"))
        payload = {
            "utforande_verksamhets_id": str(perf_op_id),
            "genomforande_referens": outplacement.order_id.origin,
            "ordernummer": outplacement.order_id.name,
            "personnummer": outplacement.partner_id.social_sec_nr.replace("-", ""),
            "unikt_id": str(uuid.uuid4()),
            "inskickad_datum": str(outplacement.fr_send_date),
            "rapportering_datum": str(outplacement.fr_report_date) if outplacement.fr_report_date else "",
            "status": outplacement.stage_id.sequence,
            "sent_inskickad": "true" if outplacement.late else "false",
            "avbrott": "true" if outplacement.interruption else "false",
            "ofullstandig": "true" if outplacement.incomplete else "false",
            "studiebesok": [],  # filled with data below
            "kompletterande_information": {
                "fraga": "komm_info",
                "svar": outplacement.complementing_information or "komm_info_03"
            }
        }
        if outplacement.partner_id:
            payload["deltagare"] = {
                "fornamn": outplacement.partner_id.firstname or "",
                "efternamn": outplacement.partner_id.lastname or "",
                "deltog_per_distans": outplacement.meeting_remote or ""
            }
        if outplacement.employee_id:
            payload["ansvarig_handledare"] = {
                "fornamn": outplacement.employee_id.firstname or "",
                "efternamn": outplacement.employee_id.lastname or "",
            }
            if outplacement.employee_id.user_id:
                payload["ansvarig_handledare"]["signatur"] = \
                    outplacement.employee_id.user_id.login
        else:
            raise ValidationError(_("Employee must be set"))
        goal_id = outplacement.main_goal_id
        if goal_id:
            payload["huvudmal"] = {
                "arbetsuppgifter_beskrivning": goal_id.job_description or "",
                "val_av_huvudmal_motivering": [],
                "fritext": goal_id.free_text or "",
                "steg": []
            }
            if goal_id.field_of_work_id:
                payload["huvudmal"]["yrkesomrade"] = goal_id.field_of_work_id.name
            if goal_id.job_id:
                payload["huvudmal"]["yrke"] = goal_id.job_id.name
            if goal_id.matches_interest:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Matchar deltagarens intressen'
                    })
            if goal_id.matches_ability:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Arbetsuppgifter matchar förmåga'
                    })
            if goal_id.market_demand:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Efterfrågan på arbetsmarknaden'
                    })
            if goal_id.complementing_education:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Kompletterar nuvarande utbildning'
                    })
            if goal_id.complementing_experience:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Kompletterar tidigare erfarenhet'
                    })
            if goal_id.other_motivation:
                payload["huvudmal"]["val_av_huvudmal_motivering"].append({
                    "typ": 'Annat',
                    "fritext": goal_id.free_text or ""
                    })
            if len(payload["huvudmal"]["val_av_huvudmal_motivering"]) < 1 \
                    and not outplacement.interruption:
                raise ValidationError(_("Motivation of main goal missing"))
            if not goal_id.step_ids and not outplacement.interruption:
                raise ValidationError(_("At least one step is required to send final report"))
            for step_id in goal_id.step_ids:
                step = {
                    "typ": step_id.step_type,
                    "niva": step_id.education_level_id.name_get()[0][1] if step_id.education_level_id else "",
                    "startdatum": str(step_id.start_date) if step_id.start_date else "",
                    "slutdatum": str(step_id.end_date) if step_id.end_date else ""
                }
                if step_id.step_type == "Studera reguljär utbildning":
                    step["namn"] = step_id.step_name or ""
                else:
                    step["namn"] = ""
                if step_id.step_type == "Lämpliga kompletterande insatser":
                    step["kompletterande_insats"] = {
                        "typ": step_id.complementing_effort_type or _("complementing effort type not set"),
                        "fritext": step_id.complementing_effort_description or ""
                    }
                elif step_id.step_type == "Annat":
                    step["fritext"] = step_id.step_name or ""
                payload['huvudmal']['steg'].append(step)
        elif not outplacement.interruption:
            raise ValidationError(_("A main goal is required to send final report"))
        goal_id = outplacement.alternative_goal_id
        if goal_id:
            payload["alternativt_mal"] = {
                "arbetsuppgifter_beskrivning": goal_id.job_description or "",
                "val_av_alternativt_mal_motivering": [],
                "fritext": goal_id.free_text or "",
                "steg": []
            }
            if goal_id.field_of_work_id:
                payload["alternativt_mal"]["yrkesomrade"] = goal_id.field_of_work_id.name

            if goal_id.job_id:
                payload["alternativt_mal"]["yrke"] = goal_id.job_id.name

            if goal_id.matches_interest:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Matchar deltagarens intressen'
                    })
            if goal_id.matches_ability:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Arbetsuppgifter matchar förmåga'
                    })
            if goal_id.market_demand:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Efterfrågan på arbetsmarknaden'
                    })
            if goal_id.complementing_education:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Kompletterar nuvarande utbildning'
                    })
            if goal_id.complementing_experience:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Kompletterar tidigare erfarenhet'
                    })
            if goal_id.other_motivation:
                payload["alternativt_mal"]["val_av_alternativt_mal_motivering"].append({
                    "typ": 'Annat',
                    "fritext": goal_id.free_text or ""
                    })
            if len(payload["alternativt_mal"]["val_av_alternativt_mal_motivering"]) < 1 \
                    and not outplacement.interruption:
                raise ValidationError(_("Motivation of alternative goal missing"))
            if not goal_id.step_ids and not outplacement.interruption:
                raise ValidationError(_("At least one step is required to send final report"))
            for step_id in goal_id.step_ids:
                step = {
                    "typ": step_id.step_type,
                    "niva": step_id.education_level_id.name_get()[0][1] if step_id.education_level_id else "",
                    "startdatum": str(step_id.start_date) if step_id.start_date else "",
                    "slutdatum": str(step_id.end_date) if step_id.end_date else ""
                }
                if step_id.step_type == "Studera reguljär utbildning":
                    step["namn"] = step_id.step_name or ""
                else:
                    step["namn"] = ""
                if step_id.step_type == "Lämpliga kompletterande insatser":
                    step["kompletterande_insats"] = {
                        "typ": step_id.complementing_effort_type,
                        "fritext": step_id.complementing_effort_description or ""
                    }
                elif step_id.step_type == "Annat":
                    step["fritext"] = step_id.step_name or ""
                payload['alternativt_mal']['steg'].append(step)
        elif not outplacement.interruption:
            raise ValidationError(_("An alternative goal is required to send final report"))
        for study_visit in outplacement.study_visit_ids:
            payload['studiebesok'].append({
                "namn": study_visit.name or "",
                "typ": study_visit.visit_type or "",
                "motivering": study_visit.reasoning or ""
            })
        _logger.debug("Final report payload: %s" % payload)
        return api.post_report(payload)
