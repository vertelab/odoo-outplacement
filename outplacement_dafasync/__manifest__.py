# -*- coding: UTF-8 -*-

################################################################################
#
#    Odoo, Open Source Management Solution
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
    'name': 'Outplacement DAFA Sync',
    'version': '12.0.1.0.2',
    'category': 'Outplacement',
    'description': """This module sync data from CRM to DAFA 
        
        partnersyncCrm2Dafa(ssn,host,user,password)
        
        This is the CRM-part of the DAFA sync\n
        
        1. v12.0.1.0.2 - AFC-2505 Sent Jobseeker info to DAFA.
        
        """,
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    "depends": [
        'partner_ssn',
        'partner_firstname',
        #'partner_education_views',
        'partner_desired_jobs',
        'partner_view_360'
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
