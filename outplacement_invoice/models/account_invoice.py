# -*- coding: utf-8 -*-

import base64
import logging
import xmltodict

from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def cron_outplacement_invoice(self):
        raindance = 'api.raindance.client.config'
        for invoice_ref in self.env[raindance].get_invoices(
                supplier_id=None, date=None):
            for invoice in self.env[raindance].get_invoice(invoice_ref):
                self.create_invoice(invoice)

    @api.model
    def create_invoice(self, invoice):
        sf = invoice.get('svefaktura')
        if sf:
            sf = xmltodict(sf)
            party = sf['Invoice']['cac:BuyerParty']['cac:Party']
            # Find or create a res_partner for buyer (AF).
            org_nr = party['cac:PartyIdentification']['cac:ID']
            res_partner = self.env['res.parter'].search(
                [('company_registry', '=', org_nr)])
            if not res_partner:
                name = party['cac:PartyName']['cbc:Name']
                org_nr = party['cac:PartyIdentification']['cac:ID']
                street = party['cac:Address']['cbc:Postbox']
                city = party['cac:Address']['CityName']
                zip_ = party['cbc:PostalZone']
                res_partner = self.env['res.partner'].create(
                    {'name': name,
                     'company_registry': org_nr,
                     'street': street,
                     'city': city,
                     'zip': zip_})

            # Create Invoice.
            current_invoice = self.env['account.invoice'].create(
                {'partner_id': res_partner.id})

            # Create attachment with raw data.
            self.env['ir.attachment'].create(
                {'res_model': 'account.invoice',
                 'res_id': current_invoice.id,
                 'datas': base64.b64encode(invoice)})

            # Find Invoice lines to add to Invoice.
            invoice_lines = sf['Invoice']['cac:InvoiceLine']
            # If its only one line it will be returned as a
            # ordered dict instead of list of ordered dicts.
            if not isinstance(invoice_lines, list):
                invoice_lines = [invoice_lines]
            # Add lines to Invoice.
            for line in invoice_lines:
                item = line['cac:Item']
                description = item['cbc:Description']
                price_info = item['cac:BasePrice']['cbc:PriceAmount']
                price = price_info['#text']
                quantity = line['cbc:InvoicedQuantity']['#text']
                self.env['account.invoice.line'].create(
                    {'invoice_id': current_invoice.id,
                     'name': description,
                     'price_unit': price,
                     'quantity': quantity})
