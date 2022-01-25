import datetime
import json
import logging
from odoo.exceptions import UserError

from odoo import api, fields, models, tools, _

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
        try:
            num_days = int(self.env["ir.config_parameter"].sudo().get_param(
                "outplacement_final_report_send.days_to_send", "41"))
        except ValueError:
            _logger.error('system parameter "outplacement_final_report_send.days_to_send" '
                          'is set to a non-numerical value')
            num_days = 41
        next_41_days = self.date_by_adding_business_days(self.service_end_date, num_days)
        canceled = self.stage_id and self.stage_id.id == self.env.ref('outplacement.cancelled_stage').id
        if canceled and today >= next_41_days:
            raise UserError(
                _("You are only allowed to send Final Report within the 60 working days after the service ended."))
        workdays_from_start = self.order_start_date + datetime.timedelta(days=15)
        if not self.main_goal_id and workdays_from_start < today:
            raise UserError(_("A main goal is required to send final report"))
        if not self.alternative_goal_id and workdays_from_start < today:
            raise UserError(_("An alternative goal is required to send final report"))

        if today <= self.service_end_date and not canceled:
            raise UserError(_("You are not allowed to send final report before service end"
                              " unless there has been an interruption"))
        if not self.jp_sent_date:
            raise UserError(_("You need to send in a joint planning "
                              "before sending in a final report"))

        client_config = self.env['ipf.final_report.client.config'].search([], limit=1)
        if client_config:
            self.fr_send_date = datetime.datetime.today().strftime("%Y-%m-%d")
            try:
                response = client_config.post_request(self)
            except Exception as e:
                # Failed to send, reset sent date.
                self.fr_send_date = False
                msg = _('Failed to send final report with error: {}')
                _logger.exception(msg.format(e))
                raise UserError(msg.format(e))
            if response.status_code != 201:
                # Failed to send, reset sent date.
                self.fr_send_date = False
                try:
                    res_dict = json.loads(response.text)
                except ValueError as e:
                    _logger.error(f"Error decoding response text: {e}")
                    raise UserError(f"Error decoding response, try again or contact support")
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
        else:
            raise UserError(_("No config found for final report"))
