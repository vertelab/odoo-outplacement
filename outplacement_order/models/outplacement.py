# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, tools, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    @api.model
    def cron_outplacement_order(self):
        client_config = self.env["ipf.showorder.client.config"].search([], limit=1)
        if not client_config:
            raise Warning(_("No client config for showorder integration"))
        if not client_config.url:
            raise Warning(_("No url configured for showorder client config"))
        if not client_config.client_id:
            raise Warning(_("No client_id configured for showorder client config"))
        if not client_config.client_secret:
            raise Warning(_("No client_secret configured for showorder client config"))

        # find outplacements to send to ordertjänsten
        outplacements = self.env["outplacement"].search(
            [("order_id.state", "!=", "done")]
        )
        for outplacement in outplacements:
            # send request
            res = client_config.get_order_id(outplacement.name)
            order_status = res.get("orderstatus")
            if not order_status:
                _logger.warn(
                    "Error in communication with ordertjänsten: res = %s" % res
                )
                raise Warning(_("Error in communication with ordertjänsten"))

            # storing this information on outplacement.stage is wierd 
            # now that we dont update outplacement.stage_id from here.
            outplacement_stage = self.env['outplacement.stage'].search([('ordertjansten_status', 'ilike', order_status)], limit=1)
            if not outplacement_stage:
                _logger.warn("Unmapped status from ordertjänsten: order status = %s" % order_status)
            else:
                # TODO: Decide if we should ever update 
                # outplacement.stage_id from this code
                # outplacement.stage_id = outplacement_stage.id
                if outplacement_stage.order_id_state:
                    if outplacement.order_id:
                        outplacement.order_id.state = outplacement_stage.order_id_state
                    else:
                        _logger.warn("Outplacement does not have a sale order: %s" % outplacement.name)
                else:
                    _logger.warn("Unmapped saleorder status: outplacement.stage = %s" % outplacement_stage)
