# -*- coding: UTF-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 Vertel AB (<https://vertel.se>).
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

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    performing_operation_ids = fields.Many2many(
        comodel_name='performing.operation',
        string='Performing Operations',
        compute='_compute_performing_operations',
        inverse='_write_performing_operations',
        search='_search_performing_operations')

    @api.multi
    def _compute_performing_operations(self):
        for employee in self:
            if employee.user_id:
                employee.performing_operation_ids = employee.user_id.performing_operation_ids  # noqa: E501

    # Special write rules are the only thing keeping this from being a
    # regular related field.
    @api.multi
    def _write_performing_operations(self):
        permission_check = self.env.user._is_system() or \
            self.env.user.has_group(
                'base_user_groups_dafa.group_dafa_org_admin_write') or \
            self.env.user.has_group(
                'base_user_groups_dafa.group_dafa_employees_write')
        if not permission_check:
            raise ValidationError(_("You are not permitted to do this"))
        for employee in self:
            if employee.user_id:
                employee.user_id.sudo().write({
                    'performing_operation_ids': [
                        (6, 0, employee.mapped('performing_operation_ids.id'))
                        ]})

    @api.model
    def _search_performing_operations(self, op, value):
        return [('user_id.performing_operation_ids', op, value)]
