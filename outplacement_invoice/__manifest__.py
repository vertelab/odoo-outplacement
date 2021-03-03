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
    'name': 'Outplacement Invoice',
    'version': '12.0.1.1.3',
    'category': 'Outplacement',
    'description': """This module listen for new invoices from Raindance...""",
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    "depends": [
        'outplacement',
        'account',
        'sale',
        'api_raindance_client',
        'res_interpreter_language',
        'res_interpreter_gender_preference',
    ],
    'data': [
        'data/cron.xml',
        'data/test.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
