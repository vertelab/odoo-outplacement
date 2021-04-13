# -*- coding: UTF-8 -*-

###############################################################################
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
###############################################################################

from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _update_last_login(self):
        # Despite model decorator, this function is executed on a user record
        try:
            xml_ids = (
                'group_dafa_admin_accounting_read',     # Hantera Ekonomi
                'group_dafa_org_admin_read',            # Hantera Organisation
                '1_line_support'                        # Servicedesk
            )
            superuser = False
            sudo_self = self.sudo()
            for xml_id in xml_ids:
                # Check if user is a member of group
                if self.has_group('base_user_groups_dafa.%s' % xml_id):
                    superuser = True
                    break
            if superuser:
                # Check if user is missing any Performing Operations
                ops = sudo_self.env['performing.operation'].search([])
                if ops - sudo_self.performing_operation_ids:
                    sudo_self.performing_operation_ids |= ops
        except Exception:
            _logger.exception(
                'Failed to update DAFA performing operations on user %s'
                % self.id)
        return super()._update_last_login()
