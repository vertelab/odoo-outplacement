# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, tools, _
from odoo.addons.sale_showorder_ipf_client.models.client_config import Client

_logger = logging.getLogger(__name__)

class Outplacement(models.Model):
    _inherit = 'outplacement'

    @api.model
    def cron_outplacement_order(self):
        for outplacement in self.env['outplacement'].search([]):
            res = self.env['ipf.showorder.client.config'].get_order_id(outplacement.name)
            # ~ 'preleminär','definitiv','avbruten','avbruten levererad',BÄR_status
            outplacement.message_post(
                    body=_(
                        """Message recieved:
        %s"""  
                    )
                    % (res)
                )
              # ~ "AVBRUTEN",
              # ~ "PRELIMINAR",
              # ~ "DEFINITIV",
              # ~ "MAKULERAD",
              # ~ "LEVERERAD",
              # ~ "KLAR"
            if res['status'] == 'preleminar':
                outplacement.status = self.env.ref('outplacement.stage_preleminar').id
                outplacement.order_id.status = 'draft'
            elif res['status'] == 'definitiv':
                outplacement.status = self.env.ref('outplacement.stage_definitiv').id
                outplacement.order_id.status = 'sale'
            elif res['status'] == 'avbruten':
                outplacement.status = self.env.ref('outplacement.stage_avbruten').id
                outplacement.order_id.status = 'cancel'
            elif res['status'] == 'avbruten_levererad':
                outplacement.status = self.env.ref('outplacement.stage_avbruten_levererad').id
                outplacement.order_id.status = 'cancel'
            else:
                pass
            
