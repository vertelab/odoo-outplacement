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


from odoo import fields, models


class ResJointPlanning(models.Model):
    _name = 'res.joint_planning'
    _description = 'Res joint planning'
    _order = "sequence, id"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")

    task_type = fields.Selection(selection=[('mandatory', 'Mandatory'),
                                            ('optional', 'Optional'), ],
                                 string='Task Type', )
    activity_id = fields.Char(string="Activity ID")
    color = fields.Integer(string='Color Index')
    planned_hours = fields.Float(
        "Planned Hours",
        help='It is the time planned to achieve the task. If this '
             'document has sub-tasks, it means the time needed to '
             'achieve this tasks and its childs.',
        track_visibility='onchange')
    send2server = fields.Boolean(string='Send to Server')
    instructions = fields.Text(string="Instructions", readonly=True)
