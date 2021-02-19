# -*- coding: utf-8 -*-
"""
Adds functions to handle invoices from Raindance server.
"""
import base64
import logging
import xmltodict

from odoo import api, models, fields, tools, _
from odoo.exceptions import Warning

# only used in tests
from odoo.addons.outplacement_invoice.static.svefaktura import SVEFAKTURA

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    """Handle Invoices from Raindance."""
    _inherit = "account.invoice"
    raindance_ref = fields.Char(string='Raindance ID')

    @api.model
    def cron_outplacement_invoice(self):
        """Cron job entry point."""
        self.outplacement_invoice(silent=True)

    @api.model
    def outplacement_invoice(self, silent=False):
        """Get invoices from raindance and proccess them."""
        raindance = 'api.raindance.client.config'
        client_config = self.env[raindance].search([], limit=1)
        if not client_config:
            raise Warning(_("No client config for raindance integration"))
        if not client_config.url:
            raise Warning(_("No url configured for raindance client config"))
        if not client_config.client_id:
            raise Warning(_("No client_id configured for raindance client config"))
        if not client_config.client_secret:
            raise Warning(_("No client_secret configured for raindance client config"))

        legacy_no = self.env["ir.config_parameter"].sudo().get_param("dafa.legacy_no")
        if not legacy_no:
            raise Warning(_("dafa.legacy_no not set in system parameters"))

        for invoice_ref in client_config.get_invoices(order_id="AKTTEST-2272")
            _logger.warn("DAER invoice_ref: %s" % invoice_ref)
            
        # for invoice_ref in client_config.get_invoices(
        #         supplier_id=legacy_no, date="200101-211231"):
        #     _logger.warn("DAER invoice_ref: %s" % invoice_ref)
            # for invoice in client_config.get_invoice(invoice_ref):
            #     self.create_invoice(invoice)

    @api.model
    def create_invoice(self, invoice):
        '''
        Process invoice in the format svefaktura.
        Takes a dict with the key svefaktura.
        '''
        sf = invoice.get('svefaktura')
        if sf:
            sf = xmltodict.parse(sf)
            invoice_ref = sf['Invoice']['ID']
            if self.env['account.invoice'].search(
                    [('raindance_ref', '=', invoice_ref)]):
                _logger.debug('Invoice already exists: %s', invoice_ref)
                return
            party = sf['Invoice']['cac:BuyerParty']['cac:Party']
            # Find or create a res_partner for buyer (AF).
            org_nr = party['cac:PartyIdentification']['cac:ID']
            res_partner = self.env['res.partner'].search(
                [('company_registry', '=', org_nr)], limit=1)
            if not res_partner:
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

    def test_data(self):
        """Returns svefaktura dict with testdata."""
        return {'svefaktura': SVEFAKTURA}
