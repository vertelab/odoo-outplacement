import datetime
import datetime
import json
import logging
from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, tools
from odoo import tools, _

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    def date_by_adding_business_days(self, from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday = 6
                continue
            business_days_to_add -= 1
        return current_date

    def send_final_report(self):
        today = datetime.date.today()
        next_41_days = self.date_by_adding_business_days(self.service_end_date, 41)
        if self.stage_id and self.stage_id.id == self.env.ref('outplacement.cancelled_stage').id or \
                today >= next_41_days:
            raise UserError(_("The Final Report can only be sent after the Service has ended."))

        if today > self.service_end_date:
            raise UserError(_("You are not allowed to send final report before service end"
                              " unless there has been an interruption"))
        if not self.jp_sent_date:
            raise UserError(_("You need to send in a joint planning "
                              "before sending in a final report"))

        already_sent = False
        if self.fr_send_date:
            already_sent = True
        if already_sent:
            raise UserError(_("You have already sent a final report for this outplacement"))

        if not self.performing_operation_id and not self.interruption:
            raise ValidationError(_("Performing operation needs to be set to send final report"))

        if not self.employee_id:
            raise ValidationError(_("Employee must be set"))
        payload = {}
        goal_id = self.main_goal_id
        if goal_id:
            payload["huvudmal"] = {
                "arbetsuppgifter_beskrivning": goal_id.job_description or "",
                "val_av_huvudmal_motivering": [],
                "fritext": goal_id.free_text or "",
                "steg": []
            }
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
                    and not self.interruption:
                raise ValidationError(_("Motivation of main goal missing"))
            if not goal_id.step_ids and not self.interruption:
                raise ValidationError(_("At least one step is required to send final report"))
        elif not self.interruption:
            raise ValidationError(_("A main goal is required to send final report"))

        goal_id = self.alternative_goal_id
        if goal_id:
            payload["alternativt_mal"] = {
                "arbetsuppgifter_beskrivning": goal_id.job_description or "",
                "val_av_alternativt_mal_motivering": [],
                "fritext": goal_id.free_text or "",
                "steg": []
            }
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
                    and not self.interruption:
                raise ValidationError(_("Motivation of alternative goal missing"))
            if not goal_id.step_ids and not self.interruption:
                raise ValidationError(_("At least one step is required to send final report"))
        elif not self.interruption:
            raise ValidationError(_("An alternative goal is required to send final report"))

        client_config = self.env['ipf.final_report.client.config'].search([], limit=1)
        if client_config:
            try:
                response = client_config.post_request(self)
                if response and response.status_code != 201:
                    res_dict = json.loads(response.text)
                    tracking_id = res_dict.get("error_id", "")
                    message = res_dict.get("message", "")
                    cause_dict = res_dict.get("cause", {})
                    code = cause_dict.get("code", _("Unknown error code"))
                    cause_message = cause_dict.get("message", _("Unknown cause"))
                    error_text = _("Error %s: %s\nCause: %s\nTracking ID: %s") % (
                    code, message, cause_message, tracking_id)
                    _logger.error("Something went wrong with sending Final Report for Outplacement %s. %s" % (
                    self.name, str(error_text)))
                    raise UserError(error_text)
                _logger.debug("Successfully created final report")
                self.fr_rejected = False
                self.message_post(body=_("Final report sent"))
                self.fr_send_date = datetime.datetime.today().strftime("%Y-%m-%d")
            except Exception as e:
                _logger.error(
                    "Something went wrong with sending Final Report for Outplacement %s. %s" % (self.name, str(e)))
        else:
            raise UserError(_("No config found for final report"))
