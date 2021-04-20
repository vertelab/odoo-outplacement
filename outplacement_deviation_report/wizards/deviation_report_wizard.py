import json
import logging
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)


class DeviationReportWizard(models.TransientModel):
    _name = "outplacement.deviation.report.wizard"

    outplacement_id = fields.Many2one(
        comodel_name="outplacement",
        string="Outplacement",
        default=lambda self: self.env["outplacement"].browse(
            self.env.context.get("active_id")
        ),
    )
    company_id = fields.Many2one(
        string="Company ID",
        comodel_name="res.company",
        default=lambda self: self.env["res.company"].search([], limit=1),
        readonly=True,
    )
    order_id = fields.Char(
        string="Order ID", readonly=True, related="outplacement_id.order_id.origin"
    )
    uniq_ref = fields.Char(string="Unique ID", default=lambda self: str(uuid.uuid4()))
    social_sec_nr = fields.Char(
        string="Social security number",
        related="outplacement_id.partner_social_sec_nr",
        readonly=True,
    )
    jobseeker_name = fields.Char(
        string="Name", related="outplacement_id.partner_name", readonly=True
    )
    responsible_id = fields.Many2one(
        related="outplacement_id.management_team_id", readonly=True
    )
    # TODO: Awaits external fix of AF_Security
    # responsible_signature = fields.Char(
    #      related="outplacement_id.management_team_id.af_signature",
    #      readonly=True,
    #      string='Responsible superviser')
    performing_operation_name = fields.Char(
        related="outplacement_id.performing_operation_id.name", readonly=True
    )
    performing_operation_nr = fields.Integer(
        related="outplacement_id.performing_operation_id.ka_nr", readonly=True
    )
    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True
    )
    deviation_date = fields.Date(default=lambda self: fields.Date.today())
    deviation_allday = fields.Boolean()
    deviation_timestart = fields.Float(default=8.0)
    deviation_timeend = fields.Float(default=17.0)
    expected_time_start = fields.Float(default=8.0)
    expected_time_end = fields.Float(default=17.0)
    deviation_type = fields.Selection(
        string="Type",
        selection=[
            ("leave", "Leave"),
            ("deviation", "Deviation"),
        ],
        required=True,
    )
    deviation_leave_code = fields.Selection(
        string="Leave Type",
        selection=[
            ("15", "Sick"),
            ("16", "Work"),
            ("26", "Childcare"),
            ("27", "Education"),
            ("17", "Unkown reason"),
            ("18", "Other known reason"),
        ],
    )
    deviation_code = fields.Selection(
        string="Deviation Type",
        selection=[
            ("19", "Rejected offered activity"),
            ("20", "Rejected offered job"),
            ("28", "Acts consciously to sabotage job prospects"),
            ("21", "Unable to benefit from the program"),
            ("22", "Missbehaved or disrupted operations"),
        ],
    )

    deviation_18_alternatives = fields.Selection(
        string="Known reason",
        selection=[
            ("1", "Dentist / Doctor"),
            ("2", "Family matter"),
            ("3", "Meeting with authority"),
            ("4", "Job interview"),
            ("5", "Other reason"),
        ],
    )
    deviation_18_other_reason = fields.Text(string="Other known reason")

    deviation_19_activity = fields.Text(
        string="What activity did the participant reject?"
    )
    deviation_19_reason = fields.Text(string="What reason did the participant give?")

    deviation_20_job = fields.Text(string="What was the rejected job?")
    deviation_20_reason = fields.Text(string="What reason did the participant give?")

    deviation_28_reason = fields.Text(
        string="How did the participant act to not get a job?"
    )

    deviation_21_reason = fields.Text(
        string="Why were they unable to benefit by the program?"
    )
    deviation_21_action = fields.Text(
        string="How did you try to adjust the program or support the participant?"
    )

    deviation_22_reason = fields.Text(string="How did they missbehave?")
    deviation_22_action = fields.Text(string="How did you try to solve the problem?")

    @api.model
    def float_to_time(self, value):
        hours, minutes = divmod(abs(value) * 60, 60)
        minutes = round(minutes)
        if minutes == 60:
            minutes = 0
            hours += 1
        if value < 0:
            return "-%02d:%02d" % (hours, minutes)
        return "%02d:%02d" % (hours, minutes)

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
        api = self.env["ipf.report.client.config"].search([], limit=1)
        if not api:
            raise UserError(_("Configuration not found"))

        legacy_no = self.env["ir.config_parameter"].sudo().get_param("dafa.legacy_no")
        if not legacy_no:
            raise UserError(_("dafa.legacy_no not set in system parameters"))
        # A013 = KVL
        service_code = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("dafa.service_code", "A013")
        )
        if self.deviation_type == "leave":
            franvaro_dict = {
                "avvikelseorsakskod": self.deviation_leave_code,
                "datum": str(self.deviation_date),
                "heldag": "true" if self.deviation_allday else "false",
                "starttid": self.start_time(),
                "sluttid": self.end_time(),
                "forvantad_narvaro": {
                    "starttid": self.float_to_time(self.expected_time_start),
                    "sluttid": self.float_to_time(self.expected_time_end),
                },
            }
        elif self.deviation_type == "deviation":
            avvikelse_dict = {
                "avvikelseorsakskod": self.deviation_code,
                "rapporteringsdatum": str(self.deviation_date),
            }

        qa_pairs = []
        payload = {
            "genomforande_referens": self.order_id,
            "id": self.uniq_ref,
            "tjanstekod": service_code,
            "datum_for_rapportering": str(self.deviation_date),
            "arbetssokande": {
                "personnummer": self.social_sec_nr.replace("-", ""),
                "fornamn": self.outplacement_id.partner_id.firstname or "",
                "efternamn": self.outplacement_id.partner_id.lastname or "",
            },
            "ansvarig_arbetsformedlare": {
                "funktionsbrevlada": self.responsible_id.email,
                "signatur": self.responsible_id.af_signature,
            },
            "leverantor": {
                "namn": self.company_id.name,
                "leverantor_id": legacy_no,
                "rapportor": {
                    "fornamn": self.user_id.firstname or "",
                    "efternamn": self.user_id.lastname or "",
                },
                "utforande_verksamhet": {
                    "namn": self.performing_operation_name,
                    "utforande_verksamhet_id": str(self.performing_operation_nr),
                },
            },
        }

        if self.deviation_code == "19" and self.deviation_19_activity:
            qa_pair = {"fraga": "19_1", "svar": self.deviation_19_activity}
            qa_pairs.append(qa_pair)
            if self.deviation_19_reason:
                qa_pair = {"fraga": "19_2", "svar": self.deviation_19_reason}
                qa_pairs.append(qa_pair)
        elif self.deviation_code == "20" and self.deviation_20_job:
            qa_pair = {"fraga": "20_1", "svar": self.deviation_20_job}
            qa_pairs.append(qa_pair)
            if self.deviation_20_reason:
                qa_pair = {"fraga": "20_2", "svar": self.deviation_20_reason}
                qa_pairs.append(qa_pair)
        elif self.deviation_code == "28" and self.deviation_28_reason:
            qa_pair = {"fraga": "28_1", "svar": self.deviation_28_reason}
            qa_pairs.append(qa_pair)
        elif self.deviation_code == "21" and self.deviation_21_reason:
            qa_pair = {"fraga": "21_1", "svar": self.deviation_21_reason}
            qa_pairs.append(qa_pair)
            if self.deviation_21_action:
                qa_pair = {"fraga": "21_2", "svar": self.deviation_21_action}
                qa_pairs.append(qa_pair)
        elif self.deviation_code == "22" and self.deviation_22_reason:
            qa_pair = {"fraga": "22_1", "svar": self.deviation_22_reason}
            qa_pairs.append(qa_pair)
            if self.deviation_22_action:
                qa_pair = {"fraga": "22_2", "svar": self.deviation_22_action}
                qa_pairs.append(qa_pair)

        if self.deviation_leave_code:

            if self.deviation_leave_code == "18" and self.deviation_18_alternatives:
                dict_18 = {}
                dict_18["typ"] = self.deviation_18_alternatives
                if self.deviation_18_other_reason:
                    dict_18["motivering"] = self.deviation_18_other_reason
                franvaro_dict["alternativ_for_kanda_orsaker"] = dict_18

            payload["franvaro"] = franvaro_dict

        if qa_pairs:
            avvikelse_dict["frageformular"] = qa_pairs
            payload["avvikelsealternativ"] = avvikelse_dict

        _logger.debug("Deviation report payload json: %s" % json.dumps(payload))

        querystring = {"client_secret": api.client_secret, "client_id": api.client_id}
        url = api.get_url("bar-avvikelserapport/v1/avvikelserapport")
        response = api.request_call(
            method="POST",
            url=url,
            payload=json.dumps(payload),
            headers=api.get_headers(),
            params=querystring,
        )
        if response.status_code not in (200, 201):
            raise UserError(_("Bad request"))
        self.outplacement_id.message_post(
            body=_("Deviation report sent")
        )
