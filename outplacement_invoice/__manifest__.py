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
    'name': 'Outplacement Invoice',
    'version': '12.0.0.0.1',
    'category': 'Project',
    'description': """This module listen for new invoices from Raindance...""",

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    "depends": [
        'outplacement',
        'account',
    ],
    'data': [
        'data/cron.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
