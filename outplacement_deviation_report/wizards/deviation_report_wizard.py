import json
import pprint
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeviationReportWizard(models.TransientModel):
    _name = 'outplacement.deviation.report.wizard'

    outplacement_id = fields.Many2one(
        comodel_name="outplacement",
        string='Outplacement',
        default=lambda self: self.env['outplacement'].browse(
            self.env.context.get('active_id')))
    uniq_ref = fields.Char(string='Unique ID',
                           default=lambda self: str(uuid.uuid4()))
    social_sec_nr = fields.Char(string="Social security number",
                                default='Replace when working',
                                readonly=True)
    # Replace with outplacement_id.first_name and last_name when its
    # implemented.
    first_name = fields.Char(related="outplacement_id.partner_name",
                             readonly=True,
                             string='First name')
    last_name = fields.Char(related="outplacement_id.partner_name",
                            readonly=True,
                            string='Last name')
    responsible_id = fields.Many2one(related="outplacement_id.employee_id",
                                     readonly=True)
    company_name = fields.Char(
        related="outplacement_id.department_id.company_id.name",
        readonly=True)
    user_id = fields.Many2one(
        'res.users', default=lambda self: self.env.user, readonly=True)
    deviation_code = fields.Selection(
        selection=[
            ("_", "***Frånvaro***"),
            ("15", "Sjuk"),
            ("16", "Arbete"),
            ("26", "VAB"),
            ("27", "Utbildning"),
            ("_", "***Avvikelse***"),
            ("17", "Okänd orsak"),
            ("18", "Annan känd orsak"),
            ("19", "Tackat nej till insats eller aktivitet"),
            ("20", "Tackat nej till erbjudet arbete"),
            ("21", "Kunde inte tillgodogöra sig programmet"),
            ("22", "Misskött sig eller stört verksamheten"),
            ])
    deviation_reason = fields.Text()
    deviation_date = fields.Date(default=lambda self: fields.Date.today())
    deviation_allday = fields.Boolean()
    deviation_timestart = fields.Float()
    deviation_timeend = fields.Float()
    expected_time_start = fields.Float()
    expected_time_end = fields.Float()
    activity_handling_company_name = fields.Char()
    activity_handling_company_id = fields.Char()
    reponsible_signature = fields.Char(
        related="outplacement_id.management_team.af_signature",
        readonly=True,
        string='Responsible superviser')

    @api.model
    def float_to_time(self, value):
        hours, minutes = divmod(abs(value) * 60, 60)
        minutes = round(minutes)
        if minutes == 60:
            minutes = 0
            hours += 1
        if value < 0:
            return '-%02d:%02d' % (hours, minutes)
        return '%02d:%02d' % (hours, minutes)

    def action_send(self):
        api = self.env['ipf.report.client.config'].search([], limit=1)
        if not api:
            raise UserError(_('Configuration not found'))
        payload = {
            "genomforande_referens": "outplacement.order_id.origin",
            "id": self.uniq_ref,
            "datum_for_rapportering": str(self.deviation_date),
            "arbetssokande": {
                "personnummer": self.social_sec_nr,
                "fornamn": self.first_name,
                "efternamn": self.last_name,
            },
            "ansvarig_arbetsformedlare": {
                "funktionsbrevlada": self.responsible_id.email,
                "signatur": self.reponsible_signature,
            },
            "leverantor": {
                "leverantorsnamn": self.company_name,
                "rapportor": {
                    "fornamn": self.first_name,
                    "efternamn": self.last_name,
                    },
                "kanummer": self.department_id,
                "utforande_verksamhet": {
                    "namn": self.activity_handling_company_name,
                    "utforande_verksamhet_id":
                        self.activity_handling_company_id,
                        },
            },
            "franvaro": {
                "orsak": self.deviation_code,
                "datum": str(self.deviation_date),
                "heldag": self.deviation_allday,
                "starttid": self.float_to_time(self.deviation_timestart),
                "sluttid": self.float_to_time(self.deviation_timeend),
                "forvantad_narvaro": {
                    "starttid": self.expected_time_start,
                    "sluttid": self.expected_time_end,
                    },
                },
            "motivering": self.deviation_reason
        }
        querystring = {"client_secret": api.client_secret,
                       "client_id": api.client_id}
        url = api.get_url('v1/genomforande-avvikelserapport-created')
        response = api.request_call(
            method="POST",
            url=url,
            payload=json.dumps(payload),
            headers=api.get_headers(),
            params=querystring)
        if response.status_code != 200:
            raise UserError(_('Bad request'))
        self.outplacement_id.message_post(
            body=f'Deviation report\n{pprint.pformat(payload)}\nResponse:'
            f'\nStatus code: {response.status_code}\n{response.text}')
