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

{
    'name': 'Order Interpreter',
    'version': '12.0.0.2',
    'category': 'Project',
    'description': """This module adds interpreter-functionality \n
    v12.0.0.2 changed the languagecodes from a full list to Tolkportalens list. AFC-1586
    """,

    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    "depends": [
        'mail',
        'hr_timesheet',
        'project',
        'task_interperator_ipf_client',
    ],
    'data': [
        'data/mail_data.xml',
        'data/cron.xml',
        'views/mail_activity_views.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
