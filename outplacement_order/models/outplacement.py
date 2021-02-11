# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    @api.model
    def cron_outplacement_order(self):
        try:
            client_config = self.env["ipf.showorder.client.config"].search([])[0]
        except:
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
            if order_status == "AVBRUTEN":
                outplacement.stage_id = self.env.ref("outplacement.cancelled_stage").id
                outplacement.order_id.state = "cancel"
            elif order_status == "AVBRUTEN_KLAR":
                outplacement.stage_id = self.env.ref("outplacement.cancelled_stage").id
                outplacement.order_id.state = "cancel"
            elif order_status == "PRELIMINAR":
                outplacement.stage_id = self.env.ref(
                    "outplacement.not_approved_stage"
                ).id
                outplacement.order_id.state = "draft"
            elif order_status == "DEFINITIV":
                outplacement.stage_id = self.env.ref("outplacement.approved_stage").id
                outplacement.order_id.state = "sale"
            elif order_status == "MAKULERAD":
                outplacement.stage_id = self.env.ref("outplacement.reject_stage").id
                outplacement.order_id.state = "cancel"
            elif order_status == "LEVERERAD":
                outplacement.stage_id = self.env.ref("outplacement.sent_stage").id
                outplacement.order_id.state = "sent"
            elif order_status == "KLAR":
                outplacement.stage_id = self.env.ref("outplacement.approved_stage").id
                outplacement.order_id.state = "done"
            else:
                # log this so we can catch errors in the future
                _logger.warn(
                    "Ordertjänsten is sending us nonsense: order status = %s"
                    % order_status
                )
