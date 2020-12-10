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
import traceback
from odoo import api
from odoo.http import request
from odoo.addons.sale_suborder_ipf_server.controllers.main import IpfServer

_logger = logging.getLogger(__name__)


class IpfServerProcess(IpfServer):

    @api.model
    def process_data(self, data):
        try:
            request.env['outplacement'].sudo().ipf_data_process(data)
        except Exception as e:
            _logger.error(e)
            traceback.print_exc()
            return False
        return True
