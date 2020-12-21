# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def cron_outplacement_invoice(self):
        for invoice in self.env['api.raindance.client.config'].get_invoices(supplier_id=None, date=None):
            pass
    
        
