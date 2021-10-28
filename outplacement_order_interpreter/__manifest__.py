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
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Order Interpreter',
    'version': '12.0.1.11.6',
    'category': 'Outplacement',
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    "depends": [
        'calendar',
        'mail',
        'hr_timesheet',
        'project',
        'task_interpreter_ipf_client',
        'res_interpreter_language',
        'res_interpreter_gender_preference',
        'res_interpreter_type',
        'res_interpreter_remote_type',
        'sale_outplacement',
        'base_user_groups_dafa'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/deliver_interpreter_view.xml',
        'data/mail_data.xml',
        'data/cron.xml',
        'views/mail_activity_views.xml',
        'views/res_partner_view.xml',
        'views/outplacement_view.xml',
        'views/assets.xml',
        'views/project_task_view.xml'
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
    'qweb': [
        'static/src/xml/activity.xml',
        'static/src/xml/booking_activity.xml'
    ],
}
