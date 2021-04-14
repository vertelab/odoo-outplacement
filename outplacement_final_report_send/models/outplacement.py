from odoo import api, fields, models, tools
from odoo import tools, _
from odoo.exceptions import Warning
import logging
import json
import datetime
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    def send_final_report(self):
        client_config = self.env['ipf.final_report.client.config'].search([], limit=1)
        self.fr_send_date = datetime.datetime.today().strftime("%Y-%m-%d")
        if client_config:
            response = client_config.post_request(self)
            if response.status_code != 201:
                res_dict = json.loads(response.text)
                tracking_id = res_dict.get("error_id", "")
                message = res_dict.get("message", "")
                cause_dict = res_dict.get("cause", {})
                code = cause_dict.get("code", _("Unknown error code"))
                cause_message = cause_dict.get("message", _("Unknown cause"))
                error_text = _("Error %s: %s\nCause: %s\nTracking ID: %s" % (code, message, cause_message, tracking_id))
                raise Warning(error_text)
            _logger.debug("Successfully created final report")
        else:
            raise Warning(_("No config found for final report"))


