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
    'version': '12.0.1.6.2',
    'category': 'Outplacement',
    'description': """This module adds interpreter-functionality \n
    v12.0.0.2 changed the languagecodes from a full list to Tolkportalens list. AFC-1586 \n
    v12.0.1.0.3 Added Category Outplacement \n
    v12.0.1.0.3 Added fields to Outplacement view \n
    v12.0.1.0.5 Hardening of interpreter-booking-parsing \n
    v12.0.1.1.0 Made some fields obligatory.\n
    v12.0.1.2.0 Added field adressat, removed edit and create from some fields.\n
    v12.0.1.3.0 Changes to validation rules.\n
    v12.0.1.4.0 Hide date due for interpreter bookings\n
    v12.0.1.4.1 Bugfix of cronjob, Handling of removal of parent task.\n
    v12.0.1.4.2 Added sequence to interpreter-booking-view.\n
    v12.0.1.5.0 Archive instead of removing.\n
    v12.0.1.5.1 Fixed crash at delivery.\n
    v12.0.1.5.2 Fixed wrong status message on cancelation.\n
    v12.0.1.5.3 Changed cancellation instruction message.\n
    v12.0.1.5.4 Fixed typo in cancelling message.\n
    v12.0.1.5.5 AFC-2028: Making fields readonly/not able to create on the fly. \n
    v12.0.1.5.6 AFC-2145: Various text formating fixes, translations \n
    V12.0.1.6.0 AFC-2125: This version adds a widget for displaying interpreter-bookings. \n
    V12.0.1.6.1 AFC-2125: This version updates a widget for displaying interpreter-bookings with activity views and new filters. \n
    V12.0.1.6.2 AFC-2217: This version adds new menu 'Interpreters' for 'Interpreter Accountants'. \n
    """,
    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
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
