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

import logging
from odoo.exceptions import Warning

from odoo import api, models, fields, tools, _

_logger = logging.getLogger(__name__)

# only used in tests
from odoo.addons.outplacement_invoice.static.svefaktura import SVEFAKTURA


class AccountInvoice(models.Model):
    """Handle Invoices from Raindance."""
    _inherit = "account.invoice"

    raindance_ref = fields.Char(string='Raindance ID')
    partner_vat = fields.Char(related="partner_id.vat", readonly=True)
    partner_company_registry = fields.Char(related="partner_id.company_registry", readonly=True)
    company_partner_id = fields.Many2one(comodel_name='res.partner', readonly=True, related='company_id.partner_id')
    company_partner_street = fields.Char(related='company_id.partner_id.street', readonly=True)
    company_partner_zip = fields.Char(related='company_id.partner_id.zip', readonly=True)
    company_partner_city = fields.Char(related='company_id.partner_id.city', readonly=True)
    company_partner_country_id = fields.Many2one(comodel_name="res.country", related='company_id.partner_id.country_id',
                                                 readonly=True)
    company_vat = fields.Char(related="company_id.vat", readonly=True)
    company_company_registry = fields.Char(related="company_id.company_registry", readonly=True)
    contract_nr = fields.Char(string="Contract nr", readonly=True)

    def test_data(self):
        """Returns svefaktura dict with testdata."""
        return {'svefaktura': SVEFAKTURA}
