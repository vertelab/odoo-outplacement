# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
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
    'name': 'Outplacement CRM Sync',
    'version': '12.0.1.0.1',
    'category': 'Outplacement',
    'description': """This module sync data to CRM ...
        
        * outplacement_crmsync.server_url  - http[s]://x.y.se
        * outplacement_crmsync.server_host - <domain>
        * outplacement_crmsync.server_port - 8069
        * outplacement_crmsync.server_db - database
        * outplacement_crmsync.server_login - userid
        * outplacement_crmsync.server_pw - password
        
        """,
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    "depends": [
        'outplacement_partner_education',
        'outplacement_partner_jobs',
        # ~ 'outplacement_partner_skills',
        'partner_firstname',
    ],
    'data': [
        'data/data.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
