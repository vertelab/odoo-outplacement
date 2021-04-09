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
    'version': '12.0.1.4.2',
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
        'outplacement',
    ],
    'data': [
        'wizards/deliver_interpreter_view.xml',
        'data/mail_data.xml',
        'data/cron.xml',
        'views/mail_activity_views.xml',
        'views/res_partner_view.xml',
        'views/outplacement_view.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
    'qweb': [
        'static/src/xml/activity.xml',
    ],
}
