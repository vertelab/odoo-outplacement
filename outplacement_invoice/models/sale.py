# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
################################################################################

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
import xmltodict
import base64
from html import unescape
from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def cron_outplacement_invoice(self):
        """Cron job entry point."""
        # for outplacement in self:
        
        # TODO: real code, uncomment
        # sale_orders = self.env['sale.order'].search([('state', 'not in', ['draft', 'done'])])
        # Tests:
        sale_orders = self.env['sale.order'].search([('id', '=', 12)])
        # _logger.warn("DAER sale_orders: %s" % sale_orders)
        for sale_order in sale_orders: 
            _logger.warn("DAER sale_order: %s" % sale_order)
            sale_order.outplacement_invoice()

    @api.one
    def outplacement_invoice(self):
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

        # TODO: real code, uncomment
        # res = client_config.get_invoices(order_id=self.outplacement_id.name)
        # tests
        # res = client_config.get_invoices(order_id="AKTTEST-2272") #finns
        # res = client_config.get_invoices(order_id="AKTTEST-4926") #oklar
        # res = client_config.get_invoices(order_id="AKTACC-506") #oklar
        # res = client_config.get_invoices(order_id="AKTTEST-4925")   #finns
        res = client_config.get_invoices(order_id="AKTTEST-4923") #finns ej än
        # _logger.warn("DAER res: %s" % res)
        # res = client_config.get_invoice(invoice_id="41209148")
        for invoice in res.get('invoices', []):
            _logger.warn("DAER invoice: %s" % invoice)
            invoice_id = invoice.get('invoice_number')
            if invoice_id:
                res_invoice = client_config.get_invoice(invoice_id=invoice_id)
                _logger.warn("DAER res_invoice: %s" % res_invoice)
                # new_invoice = self.env['account.invoice'].create_invoice(res_invoice)
                new_invoice = self.create_invoice(res_invoice)
                _logger.warn("DAER new_invoice: %s" % new_invoice)
                #this field is calculated
                # self.write({'invoice_ids': [(4, new_invoice.id, 0)]})
                # _logger.warn("DAER self: %s" % self)
                # _logger.warn("DAER self.invoice_ids: %s" % self.invoice_ids)
        # for invoice_ref in client_config.get_invoices(order_id="AKTTEST-2272"):
            # _logger.warn("DAER invoice_ref: %s" % invoice_ref)
            
    @api.one
    def create_invoice(self, invoice):
        '''
        Process invoice in the format svefaktura.
        Takes a dict with the key svefaktura.
        '''
        sf = invoice.get('svefaktura')
        if sf:
            sf = unescape(sf)
            # _logger.warn("DAER sf: %s" % sf)
            sf_dict = xmltodict.parse(sf)
            invoice_ref = sf_dict['Invoice']['ID']
            invoice = self.env['account.invoice'].search([('raindance_ref', '=', invoice_ref)])
            if invoice:
                _logger.warn('Invoice already exists: %s', invoice_ref)
                return invoice
            party = sf_dict['Invoice']['cac:BuyerParty']['cac:Party']
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

            # Find due date
            payment = sf_dict['Invoice']['cac:PaymentMeans']
            # TODO: du var här
            _logger.warn("DAER payment['cbc:DuePaymentDate']: %s" % payment['cbc:DuePaymentDate']['#text'])
            return
            due_date = payment['cbc:DuePaymentDate']['#text']
            
            # Create Invoice.
            current_invoice = self.env['account.invoice'].create(
                {
                    # TODO: add more data?
                    'partner_id': res_partner.id,
                    'date_invoice': '',
                    'date_due': '',
                    # 'raindance_ref': invoice_ref
                }
            )
            # Create attachment with raw data.
            # _logger.warn('DAER type(sf): %s', type(sf))
            self.env['ir.attachment'].create(
                {'name': 'Svefaktura',
                 'res_model': 'account.invoice',
                 'res_id': current_invoice.id,
                 'datas': base64.b64encode(bytes(sf, 'utf-8'))})

            # Find Invoice lines to add to Invoice.
            invoice_lines = sf_dict['Invoice']['cac:InvoiceLine']
            # If its only one line it will be returned as a
            # ordered dict instead of list of ordered dicts.
            if not isinstance(invoice_lines, list):
                invoice_lines = [invoice_lines]
            # _logger.warn("DAER: self.order_line: %s" % self.order_line)
            # Add lines to Invoice.
            for line in invoice_lines:
                item = line['cac:Item']
                _logger.warn("DAER item: %s" % item)
                description = item['cbc:Description']['#text']
                price_info = item['cac:BasePrice']['cbc:PriceAmount']
                price = price_info['#text']
                quantity = line['cbc:InvoicedQuantity']['#text']
                product_ext_id = item['cac:SellersItemIdentification']['cac:ID']
                # _logger.warn("DAER: product_ext_id: %s" % product_ext_id)
                
                product_mapping = {'166': 'sale_outplacement.startersattning',
                                   '167': 'sale_outplacement.slutersattning'}

                product = self.env.ref(product_mapping[product_ext_id])
                # _logger.warn("DAER: product_id: %s" % product)
                # product = self.env['product.product'].browse(product_id)
                account = self.env['account.account'].search(
                    [('code', '=', '3000')], limit=1)
                invoice_line = self.env['account.invoice.line'].create(
                    {
                        'product_id': product.id,
                        'account_id': account.id,
                        'invoice_id': current_invoice.id,
                        'name': description,
                        'price_unit': price,
                        'quantity': quantity
                    }
                )
                # find related sale order line and connect it to invoice line
                for order_line in self.order_line:
                    # _logger.warn("DAER order_line.product_id %s" % order_line.product_id)
                    if order_line.product_id == product:
                        # _logger.warn("DAER found match %s" % order_line.product_id)
                        order_line.invoice_lines = [(4, invoice_line.id, 0)]
                        break # we found what we were looking for
                
        return current_invoice