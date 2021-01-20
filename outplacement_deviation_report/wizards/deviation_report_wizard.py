import json
import logging
import pprint
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)


class DeviationReportWizard(models.TransientModel):
    _name = 'outplacement.deviation.report.wizard'

    outplacement_id = fields.Many2one(
        comodel_name="outplacement",
        string='Outplacement',
        default=lambda self: self.env['outplacement'].browse(
            self.env.context.get('active_id')))
    company_id = fields.Many2one(
        string='Company ID',
        comodel_name='res.company',
        default=lambda self: self.env['res.company'].search([], limit=1),
        readonly=True)
    order_id = fields.Char(string='Order ID',
                           readonly=True,
                           related="outplacement_id.order_id.origin")
    uniq_ref = fields.Char(string='Unique ID',
                           default=lambda self: str(uuid.uuid4()))
    # ToDo!: Fix social sec number.
    social_sec_nr = fields.Char(string="Social security number",
                                default='197012126821',
                                readonly=True)
    jobseeker_name = fields.Char(string='Name',
                                 related="outplacement_id.partner_name",
                                 readonly=True)
    responsible_id = fields.Many2one(
        related="outplacement_id.management_team_id",
        readonly=True)
    # responsible_signature = fields.Char(
    #      related="outplacement_id.management_team_id.af_signature",
    #      readonly=True,
    #      string='Responsible superviser')
    performing_operation_name = fields.Char(
        related="outplacement_id.performing_operation_id.name",
        readonly=True)
    performing_operation_nr = fields.Integer(
        related="outplacement_id.performing_operation_id.ka_nr",
        readonly=True)
    user_id = fields.Many2one(
        'res.users', default=lambda self: self.env.user, readonly=True)
    deviation_reason = fields.Text()
    deviation_date = fields.Date(default=lambda self: fields.Date.today())
    deviation_allday = fields.Boolean()
    deviation_timestart = fields.Float(default=8.0)
    deviation_timeend = fields.Float(default=17.0)
    expected_time_start = fields.Float(default=8.0)
    expected_time_end = fields.Float(default=17.0)
    deviation_code = fields.Selection(
        required=True,
        string='Deviation Type',
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

    @api.model
    def start_time(self):
        if self.deviation_allday:
            return self.float_to_time(self.expected_time_start)
        return self.float_to_time(self.deviation_timestart)

    @api.model
    def end_time(self):
        if self.deviation_allday:
            return self.float_to_time(self.expected_time_end)
        return self.float_to_time(self.deviation_timeend)

    def action_send(self):
        if self.deviation_code == '_':
            raise Warning(_("Deviation type has to be set to something "
                            "other than a header"))
        api = self.env['ipf.report.client.config'].search([], limit=1)
        if not api:
            raise UserError(_('Configuration not found'))
        payload = {
            "genomforande_referens": self.order_id,
            "id": self.uniq_ref,
            "tjanstekod": "A013",
            "datum_for_rapportering": str(self.deviation_date),
            "arbetssokande": {
                "personnummer": self.social_sec_nr,
                "fornamn": self.outplacement_id.partner_id.firstname or '',
                "efternamn": self.outplacement_id.partner_id.lastname or '',
            },
            "ansvarig_arbetsformedlare": {
                "funktionsbrevlada": self.responsible_id.email,
                "signatur": "Dummy",
            },
            "leverantor": {
                "namn": self.company_id.name,
                # Replace with self.company_id.tlr_supplier_ref
                "leverantor_id": self.company_id.partner_id.legacy_no,
                "rapportor": {
                    "fornamn": self.user_id.firstname or '',
                    "efternamn": self.user_id.lastname or '',
                    },
                "utforande_verksamhet": {
                    "namn": self.performing_operation_name,
                    "utforande_verksamhet_id":
                        str(self.performing_operation_nr),
                        },
            },
            "franvaro": {
                "avvikelseorsakskod": self.deviation_code,
                "datum": str(self.deviation_date),
                "heldag": self.deviation_allday,
                "starttid": self.start_time(),
                "sluttid": self.end_time(),
                "forvantad_narvaro": {
                    "starttid": self.float_to_time(self.expected_time_start),
                    "sluttid": self.float_to_time(self.expected_time_end),
                    },
                "motivering": self.deviation_reason or ''
                },
        }
        _logger.warn(pprint.pformat(payload))
        querystring = {"client_secret": api.client_secret,
                       "client_id": api.client_id}
        url = api.get_url('v1/genomforande-avvikelserapport-created')
        response = api.request_call(
            method="POST",
            url=url,
            payload=json.dumps(payload),
            headers=api.get_headers(),
            params=querystring)
        if response.status_code not in (200, 201):
            _logger.warning(response.text)
            _logger.warning(response.status_code)
            raise UserError(_('Bad request'))
        self.outplacement_id.message_post(
            body=f'Deviation report\n{pprint.pformat(payload)}\nResponse:'
            f'\nStatus code: {response.status_code}\n{response.text}')
