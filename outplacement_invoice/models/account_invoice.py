# -*- coding: utf-8 -*-

import base64
import logging
import xmltodict

from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    raindance_ref = fields.Char(string='Raindance ID')

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
            sf = xmltodict.parse(sf)
            invoice_ref = sf['Invoice']['ID']
            if len(self.env['account.invoice'].search(
                    [('raindance_ref', '=', invoice_ref)])):
                _logger.debug('Invoice already exists: %s', invoice_ref)
                return
            party = sf['Invoice']['cac:BuyerParty']['cac:Party']
            # Find or create a res_partner for buyer (AF).
            org_nr = party['cac:PartyIdentification']['cac:ID']
            res_partner = self.env['res.partner'].search(
                [('company_registry', '=', org_nr)], limit=1)
            if not len(res_partner):
                _logger.warn('HERE')
                name = party['cac:PartyName']['cbc:Name']
                org_nr = party['cac:PartyIdentification']['cac:ID']
                street = party['cac:Address']['cbc:Postbox']
                city = party['cac:Address']['cbc:CityName']
                zip_ = party['cac:Address']['cbc:PostalZone']
                res_partner = self.env['res.partner'].create(
                    {'name': name,
                     'company_registry': org_nr,
                     'street': street,
                     'city': city,
                     'zip': zip_})

            # Create Invoice.
            current_invoice = self.env['account.invoice'].create(
                {'partner_id': res_partner.id,
                 'raindance_ref': invoice_ref})

            # Create attachment with raw data.
            self.env['ir.attachment'].create(
                {'name': 'Svefaktura',
                 'res_model': 'account.invoice',
                 'res_id': current_invoice.id,
                 'datas': base64.b64encode(bytes(invoice['svefaktura'],
                                                 'utf-8'))})

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
                account = self.env['account.account'].search(
                    [('code', '=', '3000')], limit=1)
                self.env['account.invoice.line'].create(
                    {'account_id': account.id,
                     'invoice_id': current_invoice.id,
                     'name': description,
                     'price_unit': price,
                     'quantity': quantity})
