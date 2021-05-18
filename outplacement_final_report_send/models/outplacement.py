from odoo import api, fields, models, tools
from odoo import tools, _
from odoo.exceptions import UserError
import logging
import json
import datetime
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    def send_final_report(self):
        delta = self.service_end_date - datetime.datetime.now().date()
        if not self.interruption and delta.days > -1:
            raise UserError(_("You are not allowed to send final report before service end"
                            " unless there has been an interruption"))
        if not self.jp_sent_date:
            raise UserError(_("You need to send in a joint planning "
                              "before sending in a final report"))
        already_sent = False
        if self.fr_send_date:
            already_sent = True
        client_config = self.env['ipf.final_report.client.config'].search([], limit=1)
        self.fr_send_date = datetime.datetime.today().strftime("%Y-%m-%d")
        if client_config:
            response = client_config.post_request(self)
            if response.status_code != 201:
                if already_sent:
                    raise UserError(_("You have already sent a final report "
                                      "for this outplacement"))
                res_dict = json.loads(response.text)
                tracking_id = res_dict.get("error_id", "")
                message = res_dict.get("message", "")
                cause_dict = res_dict.get("cause", {})
                code = cause_dict.get("code", _("Unknown error code"))
                cause_message = cause_dict.get("message", _("Unknown cause"))
                error_text = _("Error %s: %s\nCause: %s\nTracking ID: %s") % (code, message, cause_message, tracking_id)
                raise UserError(error_text)
            _logger.debug("Successfully created final report")
        else:
            raise UserError(_("No config found for final report"))
        self.fr_rejected = False
        self.message_post(
            body=_("Final report sent, note that if it's not accepted "
                   "you will get that information from an administrative officer by email"))


