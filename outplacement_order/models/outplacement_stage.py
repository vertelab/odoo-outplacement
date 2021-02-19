# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class OutplacementStage(models.Model):
    _inherit = "outplacement.stage"

    ordertjansten_status = fields.Char(
        string="Ordertjänsten status",
        help="Technical name of mapped status in ordertjänsten, seperate several statuses with ','",
    )
    order_id_state = fields.Char(
        string="Säljorder status",
        help="Techincal name of mapped state on saleorders in Odoo",
    )
