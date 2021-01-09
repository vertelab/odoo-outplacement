import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError


def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]),
            ' '.join(partner_name.split()[-1:])]


class DeviationReportWizard(models.TransientModel):
    _name = 'outplacement.deviation.report.wizard'

    social_sec_nr = fields.Char(string="Social security number")
    first_name = fields.Char()
    last_name = fields.Char()
    responsible_id = fields.Char()
    company_name = fields.Char()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    deviation_reason = fields.Text()
    deviation_date = fields.Date()
    deviation_allday = fields.Boolean()
    deviation_timestart = fields.Float()
    deviation_timeend = fields.Float()
    expected_time_start = fields.Float()
    expected_time_end = fields.Float()
    activity_handling_company_name = fields.Char()
    activity_handling_company_id = fields.Char()
    reponsible_signature = fields.Char()

    @api.model
    def default_get(self, fields_list):
        res = super(DeviationReportWizard, self).default_get(fields_list)
        ctx = self._context
        if ctx.get('active_id') and ctx.get('active_model'):
            active_record = self.env[ctx['active_model']].browse(
                ctx['active_id'])
            partner = active_record.partner_id
            if partner:
                first_name, last_name = _partner_split_name(partner.name)
                res.update({
                    "first_name": first_name,
                    "last_name": last_name,
                    'responsible_id': self.env.user.email,
                    'company_name': partner.parent_id and partner.parent_id.name or '',
                })
            res['deviation_date'] = fields.Date.today()
        return res

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
            "genomforande_referens": "123456789",
            "id": "4aaaad4f-b2e0-4a99-b9a0-06bab83bf069",
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
                    "fornamn":
                        _partner_split_name(self.user_id.partner_id.name)[0],
                    "efternamn":
                        _partner_split_name(self.user_id.partner_id.name)[1]
                },
                "kanummer": "10009858",
                "utforande_verksamhet": {
                    "namn": self.activity_handling_company_name,
                    "utforande_verksamhet_id": self.activity_handling_company_id,
                },
            },
            "franvaro": {
                "orsak": self.deviation_reason,
                "datum": str(self.deviation_date),
                "heldag": self.deviation_allday,
                "starttid": self.float_to_time(self.deviation_timestart),
                "sluttid": self.float_to_time(self.deviation_timeend),
                "forvantad_narvaro": {
                    "starttid": self.expected_time_start,
                    "sluttid": self.expected_time_end,
                },
            }
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
