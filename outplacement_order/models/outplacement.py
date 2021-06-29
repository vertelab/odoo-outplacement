# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime, date
from odoo.exceptions import Warning

from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)

PRODUCT_MAPPING = {
    166: "sale_outplacement.startersattning",
    167: "sale_outplacement.slutersattning",
}


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
            [("order_id.state", "not in", ["done", "cancel"])]
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

            outplacement_stage = self.env["outplacement.stage"].search(
                [("ordertjansten_status", "ilike", order_status)], limit=1
            )
            if not outplacement_stage:
                _logger.warn(
                    "Unmapped status from ordertjänsten: order status = %s"
                    % order_status
                )
            else:
                # TODO: Decide if we should update outplacement stage in more cases
                if outplacement_stage == self.env.ref("outplacement.cancelled_stage"):
                    outplacement.stage_id = outplacement_stage.id
                    outplacement.interruption = True
                    outplacement.service_end_date = date.today()
                if outplacement_stage.order_id_state:
                    order = outplacement.order_id
                    if order:
                        order.state = outplacement_stage.order_id_state
                        confirm_date = res.get("definitivDatum", False)
                        if confirm_date:
                            order.confirmation_date = datetime.strptime(
                                confirm_date, "%Y-%m-%d"
                            )
                        try:
                            for order_line_ext in res.get("artikelList", []):
                                tlr_id = order_line_ext.get("tlrId")
                                for order_line in order.order_line:
                                    order_line_product = self.env.ref(
                                        PRODUCT_MAPPING[tlr_id]
                                    )
                                    if order_line.product_id == order_line_product:
                                        order_line.price_unit = order_line_ext.get(
                                            "nuvarandeAPris", 0
                                        )
                                        break
                        except:
                            _logger.exception("Could not update product/price from ordertjänsten.")
                    else:
                        _logger.warn(
                            "Outplacement does not have a sale order: %s"
                            % outplacement.name
                        )
                else:
                    _logger.warn(
                        "Unmapped saleorder status: outplacement.stage = %s"
                        % outplacement_stage
                    )
