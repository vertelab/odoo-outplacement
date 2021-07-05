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
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'IPF CompletionReport Client',
    'version': '12.0.0.1.2',
    'category': 'Outplacement',
    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['res_joint_planning_af', 'partner_firstname'],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
