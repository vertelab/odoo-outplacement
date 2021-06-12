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

import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    @api.model
    def _read_group_employee_ids(self, employees, domain, order):
        """ Decide what employees should show up as groups when grouping
        outplacements. Exact purpose of parameters is unknown. There is
        a lot of undocumented code to dig through before getting here.

        :param employees: An employee object, usually empty. Some sort
        of default selection?
        :param domain: A search domain for this model (outplacement).
        :param order: String containing SQL search order. Always the
        column models (hr.employee in this case) default order, but
        possibly inversed.
        """
        if self.env.user.has_group('base_user_groups_dafa.group_dafa_employees_write'):  # noqa: E501
            return employees.search(
                [(
                    'performing_operation_ids',
                    'in',
                    self.env.user.mapped('performing_operation_ids.id'))],
                order=order)
        return employees.search(
            [(
                'id',
                'in',
                self.env.user.mapped('employee_ids.id'))],
            order=order)

    @api.model
    def _read_group_performing_operation_ids(
            self, performing_operation, domain, order):
        """ Only display users performing operations. """
        return performing_operation.search(
            [(
                'id',
                'in',
                self.env.user.mapped('performing_operation_ids.id'))],
            order=order)
