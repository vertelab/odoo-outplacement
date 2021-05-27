# -*- coding: UTF-8 -*-

###############################################################################
#                                                                             #
#    OpenERP, Open Source Management Solution                                 #
#    Copyright (C) 2019 N-Development (<https://n-development.com>).          #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################


import datetime  # Used in test
import random  # Used in test
import string  # Used in test
from odoo import api, fields, models, _ 
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """
        :param view_id: Active view ID
        :param view_type: Active view type
        :param toolbar:
        :param submenu:
        :return: This function will disable CUD operations for active user if user has dafa accounting read access
        and will disable all the button from form view except preview button.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if self.env.user.has_group('base_user_groups_dafa.group_dafa_admin_accounting_read'):
            if view_type == 'form':
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//header"):
                    for item in node.getiterator('button'):
                        if item.attrib.get('string') != "Preview":
                            node.remove(item)
                for node in doc.xpath("//form"):
                    node.set('create','false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
                res['arch'] = etree.tostring(doc, encoding='unicode')
            if view_type == 'tree':
                tree_doc = etree.XML(res['arch'])
                for node in tree_doc.xpath("//tree"):
                    node.set('create','false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
                    res['arch'] = etree.tostring(tree_doc, encoding='unicode')
        return res

    @api.one
    def update_order_from_ordertjansten(self):
        res = self.env['ipf.showorder.client.config'].get_order_id(self.name)
        # ~ res = self.env['sale.order'].get_order_from_ordertjansten()
        for artikel in res.get('artikelList',[]):
            if not artikel['tlrId'] in self.order_line.mapped('product_id.tlr_ref'):
                product = self.env['product.product'].search([('tlr_ref','=',artikel['tlrId'])],limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        "tlr_ref": artikel["tlrId"],
                        "name":  artikel["namn"],
                        "list_price": artikel["nuvarandeAPris"],
      
                    })
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': product.id,
                    'qty': int(artikel['nuvarandeAntal']),
                    'forvantatantal': int(artikel['forvantatAntal']),
                    })
    @api.model
    def get_order_from_ordertjansten(self):
        return {
  "orderId": "MEET-1",
  "bestallare": "bestallaren",
  "tidigareOrderId": None,
  "bokningsId": 127523,
  "definitivDatum": None,
  "lastUpdated": "2020-11-02T15:48:11.256465",
  "orderstatus": "PRELIMINAR",
  "forsakringskassaSamarbete": True,
  "kostnadsstalle": "X75",
  "projektkod": "Projekt 1",
  "avrop": {
    "avropsId": "avropsid_3",
    "startdatum": "2020-10-01",
    "slutdatum": "2020-12-30",
    "diarieaktnummer": "d-334f"
  },
  "avtal": {
    "benamning": "Lots",
    "diarieaktnummer": "AUTO"
  },
  "artikelList": [
    {
      "id": 2,
      "tlrId": 166,
      "namn": "Startersättning",
      "miaPrisDefinitionTyp": "1",
      "nuvarandeAntal": 1,
      "forvantatAntal": 1,
      "enhet": "2",
      "nuvarandeAPris": "2000",
      "forvantatAPris": "2000",
      "kontokod": "7944",
      "verksamhetskod": "542601",
      "finansieringskod": "70227"
    },
    {
      "id": 1,
      "tlrId": 167,
      "namn": "Slutersättning",
      "miaPrisDefinitionTyp": "1",
      "nuvarandeAntal": 1,
      "forvantatAntal": 1,
      "enhet": "2",
      "nuvarandeAPris": "7000",
      "forvantatAPris": "7000",
      "kontokod": "7944",
      "verksamhetskod": "542601",
      "finansieringskod": "70227"
    }
  ],
  "bestallning": {
    "tjanst": {
      "kod": "A013",
      "namn": "Karriärvägledning"
    },
    "spar": {
      "kod": "SP1",
      "namn": "Spår 1",
      "sprak": "SE"
    },
    "omfattning": {
      "startdatum": "2020-06-01",
      "slutdatum": "2021-01-31",
      "styck": 0,
      "anvisningsgrad": 0,
      "omfattningsgrad": 0
    }
  },
  "beslut": {
    "beslutnummer": 0,
    "uppfoljningskategori": "KVR-V",
    "uppfoljningskategorikod": "U036",
    "startdatum": "2020-10-01",
    "slutdatum": "2020-12-30"
  },
  "leverantor": {
    "konto": "5113-0581",
    "ort": "Lund",
    "postnummer": "22007",
    "fakturaadress": "Box 1067",
    "leverantorsId": "mock",
    "leverantorsNamn": "AB Salgaria",
    "organistationsNummer": "5560401563",
    "utforandeverksamhetNamn": "LOTS-Test10000000",
    "utforande_verksamhet_id": "10000000"
  }
}

class Product(models.Model):
    _inherit = 'product.template'
    
    tlr_ref = fields.Char(string='Tlr ID',)
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    forvantatantal = fields.Integer(string='Förväntat antal')
    
