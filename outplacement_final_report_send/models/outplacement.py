from odoo import api, fields, models, tools
from odoo import tools, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    def send_final_report(self):
        client_config = self.env['ipf.final_report.client.config'].search([], limit=1)
        if client_config:
            response = client_config.post_request(self)
            if response.status_code != 201:
                raise Warning(response.text)
            _logger.debug("Successfully created final report")
        else:
            raise Warning(_("No config found for final report"))


