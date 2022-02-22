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

import base64
import json
import logging
import requests
import uuid
import xmltodict
from datetime import datetime
from html import unescape
from odoo.tools import pycompat

from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.invoice_lines')
    def _get_invoiced_stored(self):
        for sale_order in self:
            sale_order.invoice_count_stored = sale_order.invoice_count

    invoice_count_stored = fields.Integer(string='Invoice Count (stored)', compute='_get_invoiced_stored',
                                          readonly=True, store=True)

    @api.model
    def cron_outplacement_invoice(self):
        """Cron job entry point."""
        sale_orders = self.env['sale.order'].search(
            [('invoice_count_stored', '<', 2), ('outplacement_id', '!=', None)])
        for sale_order in sale_orders:
            try:
                sale_order.outplacement_invoice()
            except Exception:
                _logger.exception(f"Problem fetching order: {sale_order.outplacement_id.name}")

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

        res = client_config.get_invoices(order_id=self.outplacement_id.name)
        # Working test invoices
        # res = client_config.get_invoices(order_id="AKTTEST-2272")
        # res = client_config.get_invoices(order_id="AKTTEST-4925")
        # res = client_config.get_invoices(order_id="AKTTEST-4923")
        if res:
            for invoice in res.get('invoices', []):
                invoice_id = invoice.get('invoice_number')
                existing_invoice = self.env['account.invoice'].search(
                    [('raindance_ref', '=', invoice.get('ID'))])
                if invoice_id and not existing_invoice:
                    res_invoice = client_config.get_invoice(invoice_id=invoice_id)
                    self.create_invoice(res_invoice)
                elif not invoice_id:
                    _logger.error(f"There was no 'invoice_number' in invoice {invoice},"
                                  f" for outplacement {self.outplacement_id.name}")
                    if res.get('error_id', False):
                        _logger.error(f"There was an error when "
                                      f"getting invoice for "
                                      f"{self.outplacement_id.name}: "
                                      f"{res}")
        else:
            _logger.error(f"There was no response for outplacement {self.outplacement_id.name}")

    @api.one
    def create_invoice(self, invoice):
        '''
        Process invoice in the format svefaktura.
        Takes a dict with the key svefaktura.
        '''
        sf = invoice.get('svefaktura')
        if sf:
            sf = unescape(sf)
            sf_dict = xmltodict.parse(sf)
            invoice_ref = sf_dict['Invoice']['ID']
            invoice = self.env['account.invoice'].search([('raindance_ref', '=', invoice_ref)])
            if invoice:
                _logger.warning(f'Invoice already exists: {invoice_ref}')
                return invoice
            party = sf_dict['Invoice']['cac:BuyerParty']['cac:Party']
            # Find or create a res_partner for buyer (AF).
            partner_ext_id = party['cac:PartyIdentification']['cac:ID']['#text']
            try:
                res_partner = self.env.ref("__af_data__." + partner_ext_id)
            except ValueError:
                res_partner = False
            if not res_partner:
                name = party['cac:PartyName']['cbc:Name']['#text']
                vat = party['cac:PartyTaxScheme']['cac:CompanyID']
                street = False  # Steet is not sent in raindance data
                city = party['cac:Address']['cbc:CityName']['#text']
                zip_ = party['cac:Address']['cbc:PostalZone']['#text']
                country_code = party['cac:Address']['cac:Country']['cac:IdentificationCode']
                country = self.env['res.country'].search([('code', '=', country_code)])
                country_code = party['cac:Address']['cac:Country']['cac:IdentificationCode']
                bank = \
                sf_dict['Invoice']['cac:PaymentMeans']['cac:PayeeFinancialAccount']['cac:FinancialInstitutionBranch'][
                    'cac:FinancialInstitution']['cac:ID']
                bank_nr = sf_dict['Invoice']['cac:PaymentMeans']['cac:PayeeFinancialAccount']['cac:ID']

                res_partner = self.env['res.partner'].create(
                    {
                        'name': name,
                        'street': street,
                        'city': city,
                        'zip': zip_,
                        'vat': vat,
                        'country_id': country.id,
                    }
                )
                external_id = self.env['ir.model.data'].create(
                    {
                        'module': '__af_data__',
                        'model': 'res.partner',
                        'name': partner_ext_id,
                        'res_id': res_partner.id,
                    }
                )

                # check if partners bank exsists in system
                bank_id = self.env['res.bank'].search([('name', '=', bank)])
                if not bank_id:
                    bank_id = self.env['res.bank'].create(
                        {
                            'name': bank,
                        }
                    )

                # check if partners bank account already exists in system
                partner_bank_id = self.env['res.partner.bank'].search([('acc_number', '=', bank_nr)])
                if not partner_bank_id:
                    partner_bank_id = self.env['res.partner.bank'].create(
                        {
                            'acc_number': bank_nr,
                            'bank_id': bank_id.id,
                            'partner_id': res_partner.id,
                            'company_id': self.env.ref('base.main_company').id,
                        }
                    )

            # Find due date
            payment = sf_dict['Invoice']['cac:PaymentMeans']
            try:
                due_date = datetime.strptime(payment['cbc:DuePaymentDate']['#text'], '%Y-%m-%d').date()
            except KeyError:
                _logger.exception("Raindance invoice: due date not found in svefaktura-data.")
                due_date = False
            except ValueError:
                _logger.exception("Raindance invoice: due date has unexpected format in svefaktura-data.")
                due_date = False

            # Find invoice date
            try:
                invoice_date = datetime.strptime(sf_dict['Invoice']['cbc:IssueDate']['#text'], '%Y-%m-%d').date()
            except KeyError:
                _logger.exception("Raindance invoice: invoice date not found in svefaktura-data.")
                invoice_date = False
            except ValueError:
                _logger.exception("Raindance invoice: invoice date has unexpected format in svefaktura-data.")
                invoice_date = False

            # Find invoice delivery date
            try:
                date = datetime.strptime(sf_dict['Invoice']['cac:Delivery']['cbc:ActualDeliveryDateTime']['#text'],
                                         '%Y-%m-%d').date()
            except KeyError:
                _logger.exception("Raindance invoice: invoice delivery date not found in svefaktura-data.")
                date = False
            except ValueError:
                _logger.exception("Raindance invoice: invoice delivery date has unexpected format in svefaktura-data.")
                date = False

            # Try to set 30 days payment terms
            try:
                payment_terms = self.env.ref('account.account_payment_term_net')
            except ValueError:
                _logger.exception("Raindance invoice: payment terms not found in svefaktura-data.")
                payment_terms = False

            # Create Invoice.
            current_invoice = self.env['account.invoice'].create(
                {
                    'partner_id': res_partner.id,
                    'date_invoice': invoice_date,
                    'date_due': due_date,
                    'date': date,
                    'raindance_ref': invoice_ref,
                    'payment_term_id': payment_terms.id,
                    'origin': self.name,
                    'contract_nr': self.outplacement_id.file_reference_number,
                    'state': 'draft'
                }
            )

            # Create attachment with raw data.
            self.env['ir.attachment'].create(
                {
                    'name': 'Svefaktura',
                    'res_model': 'account.invoice',
                    'res_id': current_invoice.id,
                    'datas': base64.b64encode(bytes(sf, 'utf-8')),
                    'datas_fname': invoice_ref + '.xml',
                    'store_fname': invoice_ref,
                    'mimetype': 'application/xml'
                }
            )

            # Find Invoice lines to add to Invoice.
            invoice_lines = sf_dict['Invoice']['cac:InvoiceLine']
            # If its only one line it will be returned as a
            # ordered dict instead of list of ordered dicts.
            if not isinstance(invoice_lines, list):
                invoice_lines = [invoice_lines]
            # Add lines to Invoice.
            for line in invoice_lines:
                item = line['cac:Item']
                description = item['cbc:Description']['#text']
                tax_percentage = float(item['cac:TaxCategory']['cbc:Percent']['#text'])
                price_unit = float(item['cac:BasePrice']['cbc:PriceAmount']['#text'])
                price_tax = price_unit * tax_percentage / 100
                quantity = line['cbc:InvoicedQuantity']['#text']
                product_ext_id = item['cac:SellersItemIdentification']['cac:ID']

                product_mapping = {'166': 'sale_outplacement.startersattning',
                                   '167': 'sale_outplacement.slutersattning'}

                product = self.env.ref(product_mapping[product_ext_id])
                account = self.env['account.account'].search(
                    [('code', '=', '3000')], limit=1)
                invoice_line = self.env['account.invoice.line'].create(
                    {
                        'product_id': product.id,
                        'account_id': account.id,
                        'invoice_id': current_invoice.id,
                        'name': description,
                        'price_unit': price_unit,
                        'price_tax': price_tax,
                        'quantity': quantity,
                        'invoice_line_tax_ids': [(4, product.taxes_id._ids, 0)],
                    }
                )
                # find related sale order line and connect it to invoice line
                for order_line in self.order_line:
                    if order_line.product_id == product:
                        order_line.invoice_lines = [(4, invoice_line.id, 0)]
                        break  # we found what we were looking for

            # Trigger onchange on the invoice in order to force odoo
            # to calculate taxes correctly.
            current_invoice._onchange_eval('invoice_line_ids', "1", {})
            amount_tax = sf_dict['Invoice']['cac:TaxTotal']['cbc:TotalTaxAmount']['#text']
            # make sure odoo didn't calculate the tax different than
            # what the invoice says.
            current_invoice.amount_tax = amount_tax
        else:
            _logger.error(f"No 'svefaktura' in {invoice}")

        return current_invoice
