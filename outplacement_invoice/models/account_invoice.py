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
from odoo import api, models, fields, tools, _
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)

# only used in tests
from odoo.addons.outplacement_invoice.static.svefaktura import SVEFAKTURA


class AccountInvoice(models.Model):
    """Handle Invoices from Raindance."""
    _inherit = "account.invoice"

    raindance_ref = fields.Char(string='Raindance ID')

    def test_data(self):
        """Returns svefaktura dict with testdata."""
        return {'svefaktura': SVEFAKTURA}
