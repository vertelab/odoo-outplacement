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
    responsible_id = fields.Many2one('res.users')
    company_name = fields.Char()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    deviation_reason = fields.Text()
    deviation_date = fields.Date()
    deviation_allday = fields.Boolean()
    deviation_timestart = fields.Float()
    deviation_timeend = fields.Float()

    @api.model
    def default_get(self, fields_list):
        res = super(DeviationReportWizard, self).default_get(fields_list)
        ctx = self._context
        if ctx.get('active_id') and ctx.get('active_model'):
            active_record = self.env[ctx['active_model']].browse(
                ctx['active_id'])
            if 'user_id' in active_record:
                partner = active_record.user_id.partner_id
                if 'firstname' in partner and 'lastname' in partner:
                    first_name, last_name = partner.firstname, partner.lastname
                elif 'first_name' in partner and 'last_name' in partner:
                    first_name = partner.first_name
                    last_name = partner.last_name
                else:
                    first_name, last_name = _partner_split_name(
                        partner.name)
                resp_id = partner.user_id and partner.user_id.id or False
                res.update({
                    "first_name": first_name,
                    "last_name": last_name,
                    'responsible_id': resp_id,
                    'company_name': self.user_id.company_id.name,
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
                "funktionsbrevlada": self.responsible_id.email
            },
            "leverantor": {
                "leverantorsnamn": self.company_name,
                "rapportor": {
                    "fornamn":
                        _partner_split_name(self.user_id.partner_id.name)[0],
                    "efternamn":
                        _partner_split_name(self.user_id.partner_id.name)[1]
                },
                "kanummer": "10009858"
            },
            "franvaro": {
                "orsak": self.deviation_reason,
                "datum": str(self.deviation_date),
                "heldag": self.deviation_allday,
                "starttid": self.float_to_time(self.deviation_timestart),
                "sluttid": self.float_to_time(self.deviation_timeend)
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
